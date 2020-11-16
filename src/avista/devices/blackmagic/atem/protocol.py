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
        self.transport.connect(self.device.host, self.device.port)
        self._is_initialised = False

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

    def datagramReceived(self, datagram, _):
        packet = Packet.parse(datagram)
        if packet:
            self._current_uid = packet.uid
            self.log.debug('Received packet {packet}', packet=packet)
            if packet.payload:
                commands = self._command_parser.parse_commands(packet.payload)
                if commands:
                    print(commands)

            if packet.bitmask & (PacketType.HELLO_PACKET | PacketType.ACK_REQUEST):
                self._is_initialised = False
                ack = Packet.create(
                    PacketType.ACK,
                    self._current_uid,
                    0
                )
                self.send_packet(ack)
                self._is_initialised = True

    def send_packet(self, packet):
        if not (packet.bitmask & (PacketType.HELLO_PACKET | PacketType.ACK)):
            self._packet_counter += 1
            packet.package_id = self._packet_counter
        self.log.debug('Sending packet {packet}', packet=packet)
        self.transport.write(packet.to_bytes())
