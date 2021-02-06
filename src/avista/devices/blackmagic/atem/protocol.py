from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

from .commands import CommandParser
from .packet import Packet, PacketType, SIZE_OF_HEADER

import struct


class ATEMProtocol(DatagramProtocol):
    def __init__(self, device):
        self.device = device
        self.log = device.log
        self._command_parser = CommandParser()

        self._packet_counter = 0
        self._current_uuid = 0x1337
        self._is_initialised = False

    def startProtocol(self):
        if not self._is_initialised:
            self.log.info(
                'Trying to connect to ATEM on {host}:{port}',
                host=self.device.host,
                port=self.device.port
            )

            if self.transport and not self.transport._connectedAddr:
                self.transport.connect(self.device.host, self.device.port)

            payload = struct.pack('!I', 0x01000000)
            payload += struct.pack('!I', 0x00)

            p = Packet.create(
                PacketType.HELLO_PACKET,
                self._current_uuid,
                0,
                0,
                payload
            )
            self.send_packet(p)

            # Send another hello in 10s if we haven't connected by then
            reactor.callLater(
                10.0,
                self.startProtocol
            )

    def datagramReceived(self, datagram, _):
        packet = Packet.parse(datagram)
        if packet:
            self._current_uid = packet.uid
            self.log.debug('Received packet {packet}', packet=packet)
            if packet.payload:
                commands = self._command_parser.parse_commands(packet.payload)
                if commands:
                    for command in commands:
                        self.device.receive_command(command)

            if packet.bitmask & (PacketType.HELLO_PACKET | PacketType.ACK_REQUEST):
                if not self._is_initialised:
                    self._is_initialised = True
                    self.log.info(
                        'Connection to ATEM at {host}:{port} established',
                        host=self.device.host,
                        port=self.device.port
                    )
                ack = Packet.create(
                    PacketType.ACK,
                    self._current_uid,
                    0
                )
                self.send_packet(ack)

    def send_packet(self, packet):
        if not (packet.bitmask & (PacketType.HELLO_PACKET | PacketType.ACK)):
            self._packet_counter += 1
            packet.package_id = self._packet_counter
        self.log.debug('Sending packet {packet}', packet=packet)
        self.transport.write(packet.to_bytes())

    def send_command(self, command):
        packet = Packet.create(
            PacketType.ACK_REQUEST,
            self._current_uid,
            0,
            payload=command.to_bytes()
        )
        self.send_packet(packet)
