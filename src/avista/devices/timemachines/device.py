from avista.devices.net import NetworkDevice
from avista.devices.timemachines.protocol import TMProtocol
from twisted.internet import reactor


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

        print(self._state)
