from avista.core import expose
from avista.devices.net import NetworkDevice
from twisted.protocols.basic import LineOnlyReceiver


class HyperDeckProtocol(LineOnlyReceiver):

    def __init__(self, device):
        self.device = device
        self._multiline_buffer = []
        self._multiline_mode = False

    def connectionMade(self):
        self.sendLine(b'notify: transport: true slot: true')

    def lineReceived(self, line):
        if self._multiline_mode:
            if len(line) > 0:
                self._multiline_buffer.append(line.decode('utf-8'))
            else:
                self._handle_message(self._multiline_buffer)
                self._multiline_buffer.clear()
                self._multiline_mode = False
        else:
            if len(line) > 0 and line[-1] == 58:  # 58 == :
                self._multiline_mode = True
                self._multiline_buffer.append(line.decode('utf-8'))
            else:
                self._handle_message([line.decode('utf-8')])

    def _handle_message(self, lines):
        msg_code = lines[0][0:3]
        lines[0] = lines[0][4:]
        payload = {}
        if len(lines) > 1:
            for line in lines[1:]:
                if ': ' in line:
                    key, value = line.split(': ')
                    payload[key] = value

        handler_method_name = "_recv_{}".format(msg_code)
        if hasattr(self.device, handler_method_name) and callable(getattr(self.device, handler_method_name)):
            getattr(self.device, handler_method_name)(payload)
        else:
            self.device.log.warn("Unhandled packet type {code}: {line1} {payload}", code=msg_code, line1=lines[0], payload=payload)


class HyperDeck(NetworkDevice):

    def __init__(self, config):
        super().__init__(config)
        self._state = {}

    def get_protocol(self):
        if not self.protocol:
            self.protocol = HyperDeckProtocol(self)
        return self.protocol

    def _recv_200(self, payload):
        pass  # 200 is 'OK'

    def _recv_500(self, payload):
        self._state['connection'] = payload

    @expose
    def play(self, single_clip=None, speed=None, loop=None):
        if single_clip is None and speed is None and loop is None:
            self.protocol.sendLine(b'play')
        else:
            cmd = 'play: '
            if single_clip is not None:
                cmd += 'single clip: {} '.format('true' if single_clip else 'false')
            if speed is not None:
                cmd += 'speed: {} '.format(speed)
            if loop is not None:
                cmd += 'loop: {} '.format('true' if loop else 'false')
            self.protocol.sendLine(cmd.strip().encode('utf-8'))
