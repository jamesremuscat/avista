from avista.core import Device, expose
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory


class NetworkProtocolFactory(ReconnectingClientFactory):
    def __init__(self, device):
        self.device = device

    def buildProtocol(self, _):
        self.resetDelay()
        return self.device.get_protocol()

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)
        super().clientConnectionLost(connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
        super().clientConnectionFailed(connector, reason)


class NetworkDevice(Device):
    def __init__(self, config):
        self.protocol = None
        super().__init__(config)
        self.host = config.extra['host']
        self.port = config.extra['port']
        self.always_powered = config.extra.get('alwaysPowered')

        self._connection = None

        if self.always_powered:
            self.after_power_on()

    def get_protocol(self):
        return None

    def after_power_on(self):

        factory = NetworkProtocolFactory(self)

        self._connection = reactor.connectTCP(
            self.host,
            self.port,
            factory
        )

    def before_power_off(self):
        if self._connection:
            self._connection.disconnect()
