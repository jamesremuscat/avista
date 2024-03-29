from recordclass import recordclass

import struct


SIZE_OF_HEADER = 12


class PacketType(object):
    NULL_COMMAND = 0x00
    ACK_REQUEST = 0x01
    HELLO_PACKET = 0x02
    RESEND = 0x04
    UNDEFINED = 0x08
    ACK = 0x10


class Packet(recordclass('Packet', ['bitmask', 'size', 'uid', 'ack_id', 'package_id', 'payload'])):
    @staticmethod
    def parse(datagram):
        if len(datagram) >= SIZE_OF_HEADER:
            bitmask = struct.unpack('B', datagram[0:1])[0] >> 3
            return Packet(
                bitmask,
                struct.unpack('!H', datagram[0:2])[0] & 0x07FF,
                struct.unpack('!H', datagram[2:4])[0],
                struct.unpack('!H', datagram[4:6])[0],
                struct.unpack('!H', datagram[10:12])[0],
                datagram[12:]
            )

    @staticmethod
    def create(bitmask, uid, ack_id, package_id=0, payload=b''):
        return Packet(
            bitmask,
            len(payload) + SIZE_OF_HEADER,
            uid,
            ack_id,
            package_id,
            payload
        )

    def to_bytes(self):
        buffer = b''
        payload_size = len(self.payload)

        if self.bitmask & PacketType.ACK_REQUEST:
            payload_size += 4

        val = self.bitmask << 11
        val |= (payload_size + SIZE_OF_HEADER)
        buffer += struct.pack('!H', val)
        buffer += struct.pack('!H', self.uid)
        buffer += struct.pack('!H', self.ack_id)
        if not (self.bitmask & PacketType.HELLO_PACKET):
            buffer += struct.pack('!I', 0)
        buffer += struct.pack('!H', self.package_id)
        if self.payload:
            buffer += struct.pack('!H', payload_size)
            buffer += b'\x00\x00'
            buffer += self.payload
        return buffer
