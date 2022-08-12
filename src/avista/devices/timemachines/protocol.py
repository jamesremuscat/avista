from twisted.internet.protocol import DatagramProtocol

from avista.devices.timemachines.packet import QueryResponse


class TMProtocol(DatagramProtocol):

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def startProtocol(self):
        for clock in self.manager._clocks:
            self.transport.write(
                b'\xA1\x04\xB2',
                (clock, self.manager.port)
            )

    def datagramReceived(self, datagram, source):
        if len(datagram) > 1:
            parsed = QueryResponse.parse(datagram)
            self.manager._handle_query_response(
                source[0],
                parsed
            )
