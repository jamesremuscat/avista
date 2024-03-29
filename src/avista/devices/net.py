from avista.core import Device, expose
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory


class NotConnectedException(Exception):
    pass


class NetworkProtocolFactory(ReconnectingClientFactory):
    maxDelay = 30

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
    default_port = None

    def __init__(self, config):
        self.protocol = None
        super().__init__(config)
        self.host = config.extra.get('host')
        self.port = config.extra.get('port', self.default_port)
        self.always_powered = config.extra.get('alwaysPowered')

        self._connection = None
        self._factory = None

        if self.always_powered:
            self._connect()

    def get_protocol(self):
        if not self.protocol:
            self.protocol = self.create_protocol()
        return self.protocol

    def create_protocol(self):
        return None

    def send(self, data):
        if self.get_protocol():
            self.get_protocol().send(data)
        else:
            raise NotConnectedException()

    def _connect(self):
        self.log.info(f'Attempting to connect to {self.host}:{self.port}')
        self._factory = NetworkProtocolFactory(self)

        self._connection = reactor.connectTCP(
            self.host,
            self.port,
            self._factory
        )

    def after_power_on(self):
        if not self.always_powered and not self._connection:
            self._connect()

    def before_power_off(self):
        if not self.always_powered:
            if self._factory:
                self._factory.stopTrying()
                self._factory = None
            if self._connection:
                if hasattr(self._connection, 'disconnect'):  # TCP
                    self._connection.disconnect()
                elif hasattr(self._connection, 'stopListening'):  # UDP
                    self._connection.stopListening()
                self._connection = None
            self.protocol = None
