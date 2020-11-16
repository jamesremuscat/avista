from avista.devices.net import NetworkDevice
from twisted.internet import reactor

from .protocol import ATEMProtocol


class ATEM(NetworkDevice):
    default_port = 9910

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
