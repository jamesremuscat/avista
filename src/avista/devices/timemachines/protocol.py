from twisted.internet.protocol import DatagramProtocol

from avista.devices.timemachines.packet import QueryResponse


class MalformedPacketException(Exception):
    pass


COMMAND_ACK = b'A\x00'


class TMProtocol(DatagramProtocol):

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def startProtocol(self):
        for clock in self.manager._clocks:
            self.query_clock(clock)

    def query_clock(self, clock):
        self.transport.write(
            b'\xA1\x04\xB2',
            (clock, self.manager.port)
        )

    def datagramReceived(self, datagram, source):
        print(datagram.hex())
        if len(datagram) > 2:
            parsed = QueryResponse.parse(datagram)
            self.manager._handle_query_response(
                source[0],
                parsed
            )
        elif datagram != COMMAND_ACK:
            raise MalformedPacketException(datagram)

    def send_packet(self, destination_ip, data):
        self.transport.write(
            data,
            (destination_ip, self.manager.port)
        )
        self.query_clock(destination_ip)
