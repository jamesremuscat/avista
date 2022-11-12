from avista.core import expose
from avista.devices.net import NetworkDevice
from twisted.internet.protocol import Protocol

# Support for Dingtian's excellent range of smart relay boards
# https://www.dingtian-tech.com/
# This is only a fraction of what these boards can do; and they speak a huge
# variety of protocols.


class StringProtocol(Protocol):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler

    def connectionMade(self):
        self.send(b'00')

    def dataReceived(self, data):
        parts = data.decode('utf-8').split(':')

        if len(parts) == 3:
            self.handler._handle_state_packet(
                list(parts[0]),
                list(parts[1])
            )

    def send(self, data):
        if self.transport:
            self.transport.write(data)


class EthernetRelay(NetworkDevice):
    default_port = 60001

    def __init__(self, config):
        super().__init__(config)
        self._state = {
            'relays': [],
            'inputs': []
        }

    def create_protocol(self):
        return StringProtocol(self)

    def _handle_state_packet(self, relay_states, input_states):
        self._state['relays'] = list(map(lambda state: state == '1', relay_states))
        self._state['inputs'] = list(map(lambda state: state == '1', input_states))

        self.broadcast_device_message(
            'state',
            self._state,
            retain=True
        )

    @expose
    def turnOn(self, channel):
        if channel <= len(self._state['relays']):
            protocol = self.get_protocol()
            if protocol:
                protocol.send(b'1' + str(channel).encode('utf-8') + b'\x00')

    @expose
    def turnOff(self, channel):
        if channel <= len(self._state['relays']):
            protocol = self.get_protocol()
            if protocol:
                protocol.send(b'2' + str(channel).encode('utf-8') + b'\x00')
