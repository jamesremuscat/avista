from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall

from .commands import CommandParser
from .packet import Packet, PacketType, SIZE_OF_HEADER

import struct
import time


class CommandVersionMismatchError(Exception):
    pass


class ATEMProtocol(DatagramProtocol):
    def __init__(self, device):
        self.device = device
        self.log = device.log
        self._command_parser = CommandParser()

        self._packet_counter = 0
        self._current_uuid = 0x1337
        self._is_initialised = False

        self._last_received = None
        self._timeout = device.config.extra.get('timeout', 10)
        self._timeout_checker = LoopingCall(self._check_timeout)

    def startProtocol(self):
        if self.transport and not self._is_initialised:
            self.log.info(
                'Trying to connect to ATEM on {host}:{port}',
                host=self.device.host,
                port=self.device.port
            )

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

    def _check_timeout(self):
        now = time.time()
        if self._is_initialised and self._last_received and self._last_received + self._timeout < now:
            self.log.warn(
                'Connection to ATEM at {host}:{port} timed out (waited {delta:.1f} secs)',
                host=self.device.host,
                port=self.device.port,
                delta=now - self._last_received
            )
            self._timeout_checker.stop()
            self._packet_counter = 0
            self._current_uuid = 0x1337
            self._is_initialised = False
            self._last_received = None
            self.startProtocol()

    def datagramReceived(self, datagram, _):
        packet = Packet.parse(datagram)
        if packet:
            self._current_uid = packet.uid
            self.log.debug('Received packet {packet}', packet=packet)
            self._last_received = time.time()
            if packet.payload:
                commands = self._command_parser.parse_commands(packet.payload)
                if commands:
                    for command in commands:
                        self.device.receive_command(command)

            if packet.bitmask & PacketType.HELLO_PACKET:
                self._is_initialised = False

                ack = Packet.create(
                    PacketType.ACK,
                    self._current_uid,
                    0
                )
                self.send_packet(ack)
            elif packet.bitmask & PacketType.ACK_REQUEST:
                if not self._is_initialised:
                    self._is_initialised = True
                    self._timeout_checker.start(10)

                ack = Packet.create(
                    PacketType.ACK,
                    self._current_uid,
                    packet.package_id
                )
                self.send_packet(ack)

    def send_packet(self, packet):
        if not (packet.bitmask & (PacketType.HELLO_PACKET | PacketType.ACK)):
            self._packet_counter += 1
            if self._packet_counter >= 32768:
                self._packet_counter = 0
            packet.package_id = self._packet_counter
        self.log.debug('Sending packet {packet} => {b}', packet=packet, b=packet.to_bytes())
        self.transport.write(packet.to_bytes(), (self.device.host, self.device.port))

    def send_command(self, command):
        if self._command_parser._version:
            if hasattr(command, 'maximum_version'):
                if command.maximum_version < self._command_parser._version:
                    raise CommandVersionMismatchError()

            if hasattr(command, 'minimum_version'):
                if command.minimum_version > self._command_parser._version:
                    raise CommandVersionMismatchError()

        packet = Packet.create(
            PacketType.ACK_REQUEST,
            self._current_uid,
            0,
            payload=command.to_bytes()
        )
        self.send_packet(packet)
