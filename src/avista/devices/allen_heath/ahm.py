from avista.core import expose
from avista.devices.net import NetworkDevice
from mido import Message, Parser
from twisted.internet.protocol import Protocol
from twisted.internet.task import LoopingCall


SYSEX_HEADER = b'\x00\x00\x1A\x50\x12\x01\x00'
SYSEX_HEADER_LENGTH = len(SYSEX_HEADER)

MAX_CHANNELS = 64
MAX_CONTROL_GROUPS = 32

INPUT_TYPE = b'\x00'
ZONE_TYPE = b'\x01'
CONTROL_GROUP_TYPE = b'\x02'


class AHMProtocol(Protocol):
    def __init__(self, onmessage) -> None:
        super().__init__()
        self.onmessage = onmessage
        self._parser = Parser()

    def connectionMade(self):
        print('Connected')

        # Get state of inputs
        for i in range(MAX_CHANNELS):
            msg = Message('sysex', data=SYSEX_HEADER + INPUT_TYPE + b'\x09' + i.to_bytes(1, 'big'))
            self.send(bytes(msg.bytes()))

        # Get state of zones
        for i in range(MAX_CHANNELS):
            self.send(bytes(Message('sysex', data=SYSEX_HEADER + ZONE_TYPE + b'\x09' + i.to_bytes(1, 'big')).bytes()))
            self.send(bytes(Message('sysex', data=SYSEX_HEADER + ZONE_TYPE + b'\x01\x0F\x08' + i.to_bytes(1, 'big')).bytes()))

        # Get state of control groups
        for i in range(MAX_CONTROL_GROUPS):
            msg = Message('sysex', data=SYSEX_HEADER + b'\x02\x09' + i.to_bytes(1, 'big'))
            self.send(bytes(msg.bytes()))

    def dataReceived(self, data):
        self._parser.feed(data)
        while self._parser.pending():
            self.onmessage(self._parser.get_message())

    def send(self, data):
        if self.transport:
            self.transport.write(data)


class AHM(NetworkDevice):
    default_port = 51325

    def __init__(self, config):
        super().__init__(config)
        self._reset_state()
        self._publisher = LoopingCall(self._maybe_publish_update)

    def _reset_state(self):
        self._state = {
            'controlGroups': [
                {
                    'name': ''
                } for _ in range(MAX_CHANNELS)
            ],
            'inputs': [
                {
                    'name': ''
                } for _ in range(MAX_CHANNELS)
            ],
            'zones': [
                {
                    'name': ''
                } for _ in range(MAX_CHANNELS + 1)
            ]
        }
        self._modified = True
        self._maybe_publish_update()

    def create_protocol(self):
        return AHMProtocol(self.handle_message)

    def after_power_on(self):
        self._publisher.start(0.5)
        return super().after_power_on()

    def before_power_off(self):
        self._publisher.stop()
        return super().before_power_off()

    def handle_message(self, message):
        data = bytes(message.data)
        handled = False
        if (data[0:SYSEX_HEADER_LENGTH]) == SYSEX_HEADER:
            payload = data[SYSEX_HEADER_LENGTH:]
            match payload[1]:
                case 0x08:
                    self._handle_source_selector(payload)
                    handled = True
                case 0x0A:
                    self._handle_channel_name(payload)
                    handled = True
                case _:
                    print(f'Unknown data packet type: {payload[1]} (full payload {payload})')
        if handled:
            self._modified = True

    def _maybe_publish_update(self):
        if self._modified:
            # print(self._state)
            self.broadcast_device_message(
                'state',
                self._state,
                retain=True
            )
            self._modified = False

    def _handle_channel_name(self, data):
        if data[0] == 0:
            self._state['inputs'][data[2]]['name'] = data[3:].decode('utf-8').replace('\x00', '')
        elif data[0] == 1:
            self._state['zones'][data[2]]['name'] = data[3:].decode('utf-8').replace('\x00', '')
        elif data[0] == 2:
            self._state['controlGroups'][data[2]]['name'] = data[3:].decode('utf-8').replace('\x00', '')
        else:
            print(f'Unknown type for channel name: {data[0]}')

    def _handle_source_selector(self, data):
        zone = self._state['zones'][data[2]]

        if len(data) > 15:
            zone['currentSource'] = data[4]
            zone['sources'] = []

            num_sources = data[3]
            source_names = data[5 + num_sources:].split(b'\x00')
            for source in range(num_sources):
                zone['sources'].append(
                    {
                        'color': data[5 + source],
                        'name': source_names[source].decode('utf-8')
                    }
                )
        else:
            zone['currentSource'] = data[3]

    @expose
    def set_zone_source(self, zone, sourceIndex):
        msg = bytes(Message(
            'sysex',
            data=SYSEX_HEADER + b'\x00\x08' + zone.to_bytes(1, 'big') + sourceIndex.to_bytes(1, 'big')
        ).bytes())
        self.send(msg)
