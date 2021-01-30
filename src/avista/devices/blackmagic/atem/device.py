from avista.devices.net import NetworkDevice
from twisted.internet import reactor

from .protocol import ATEMProtocol


class ATEM(NetworkDevice):
    default_port = 9910

    def __init__(self, *args, **kwargs):
        self._state = {}
        super(ATEM, self).__init__(*args, **kwargs)

    def create_protocol(self):
        return ATEMProtocol(self)

    def _connect(self):
        protocol = self.get_protocol()
        self._connection = reactor.listenUDP(
            self.port,
            protocol
        )

    def before_power_off(self):
        if not self.always_powered:
            if self._connection:
                self._connection.stopListening()
            self.protocol = None

    def receive_command(self, command):
        new_state = command.apply_to_state(self._state)
        self._state = new_state
        if new_state.get('state', {}).get('initialized'):
            print(self._state)
