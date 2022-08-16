from avista.core import expose
from avista.devices.net import NetworkDevice
from avista.devices.timemachines.protocol import TMProtocol
from twisted.internet import reactor


class UnknownClockException(Exception):
    pass


class Manager(NetworkDevice):
    default_port = 7372

    def __init__(self, config):
        self._clocks = config.extra.get('clocks', '').split(',')
        self._state = {
            'clocks': {}
        }
        super().__init__(config)

    def create_protocol(self):
        return TMProtocol(self)

    def _connect(self):
        protocol = self.get_protocol()
        self._connection = reactor.listenUDP(
            self.port,
            protocol
        )

    def _handle_query_response(self, source, data):
        self._state['clocks'][source] = {
            'name': data.name,
            'display': {
                'mode': str(data.display.mode),
                'timer_running': data.display.running
            }
        }

        self.broadcast_device_message(
            'state',
            self._state,
            retain=True
        )

    def _send(self, clock_ip, data):
        protocol = self.get_protocol()
        if clock_ip in self._state['clocks']:
            protocol.send_packet(clock_ip, data)
        else:
            raise UnknownClockException(clock_ip)

    def show_time(self, clock_ip):
        self._send(
            clock_ip,
            b'\xA8\x01\x00'
        )

    # Count-up timer methods

    @expose
    def show_up_timer(self, clock_ip, use_tenths=False):
        self._send(
            clock_ip,
            b'\xA2' + (b'\x00' if use_tenths else b'\x01') + b'\x00'
        )

    @expose
    def start_up_timer(self, clock_ip):
        self._send(clock_ip, b'\xA3\x01\x00')

    @expose
    def pause_up_timer(self, clock_ip):
        self._send(clock_ip, b'\xA3\x00\x00')

    @expose
    def reset_up_timer(self, clock_ip, use_tenths=False):
        self._send(
            clock_ip,
            b'\xA4' + (b'\x00' if use_tenths else b'\x01') + b'\x00'
        )

    # Countdown timer methods

    def _set_countdown_timer(self, clock_ip, show, days=0, hours=0, minutes=0, seconds=0, tenths=0, alarm_duration=0, use_tenths=False):
        b = [0xA5 if show else 0xA7]
        b.append(0 if use_tenths else 1)
        b += [hours, minutes, seconds, tenths]
        b += [1, alarm_duration] if alarm_duration > 0 else [0, 0]
        b += [days & 0x15, (days >> 4) & 0x15]

        self._send(clock_ip, bytes(b))

    @expose
    def show_countdown_timer(self, clock_ip, days=0, hours=0, minutes=0, seconds=0, tenths=0, alarm_duration=0, use_tenths=False):
        self._set_countdown_timer(clock_ip, True, days, hours, minutes, seconds, tenths, alarm_duration, use_tenths)

    @expose
    def start_countdown_timer(self, clock_ip):
        self._send(clock_ip, b'\xA6\x01\x00')

    @expose
    def pause_countdown_timer(self, clock_ip):
        self._send(clock_ip, b'\xA6\x00\x00')

    @expose
    def reset_countdown_timer(self, clock_ip, days=0, hours=0, minutes=0, seconds=0, tenths=0, alarm_duration=0, use_tenths=False):
        self._set_countdown_timer(clock_ip, False, days, hours, minutes, seconds, tenths, alarm_duration, use_tenths)

    # Colour setting (volatile - only way to set permanently is via HTTP AFAICT)

    @expose
    def set_display_color(self, clock_ip, red, green, blue, hour_red=None, hour_green=None, hour_blue=None):
        if hour_red is None:
            hour_red = red
        if hour_green is None:
            hour_green = green
        if hour_blue is None:
            hour_blue = blue

        b = [
            0xB6,
            red, green, blue,
            hour_red, hour_green, hour_blue
        ]

        self._send(clock_ip, bytes(b))
