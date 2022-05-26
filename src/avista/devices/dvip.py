from avista.devices.net import NetworkDevice
from avista.devices.visca import VISCACameraBase
from twisted.internet.defer import Deferred
from twisted.protocols.basic import LineReceiver


def _split_response(response_bytes):
    packets = []

    remaining = map(ord, response_bytes[2:])
    while True:
        try:
            idx = remaining.index(0xFF)
            packet, remaining = remaining[0:idx + 1], remaining[idx + 1:]
            packets.append(packet)
        except ValueError:
            return packets


class DVIPProtocol(LineReceiver):
    def __init__(self, handler):
        super().__init__()
        self.setRawMode()
        self.handler = handler

    def connectionMade(self):
        self.device.log.info('Connected to DVIP device')

    def rawDataReceived(self, data):
        packets = _split_response(data)
        for packet in packets:
            responseType = (packet[1] & 0x70) >> 4
            source = (packet[0] >> 4) - 8

            if source == self.camera_id:
                if responseType == 4:
                    self.handler.on_ack()
                elif responseType == 5:
                    if packet[1] & 0x0F == 0:
                        self.handler.on_response(packet[2:-1])
                    else:
                        self.handler.on_complete()
                elif responseType == 6:
                    self.handler.on_error(packet[2])


class DVIPCamera(NetworkDevice, VISCACameraBase):
    def get_protocol(self):
        return DVIPProtocol(self)

    async def sendVISCA(self, visca, with_lock=None):
        data = b'\x81' + visca + b'\xFF'
        length = len(data) + 2

        return await self._sendVISCARaw(
            bytes([(length >> 8), (length & 0xFF)] + data),
            with_lock
        )
