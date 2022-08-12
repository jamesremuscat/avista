from avista.devices.net import NetworkDevice, NotConnectedException
from avista.devices.visca import VISCACameraBase
from twisted.internet.protocol import Protocol


def _split_response(response_bytes):
    packets = []

    remaining = response_bytes[2:]
    while True:
        try:
            idx = remaining.index(0xFF)
            packet, remaining = remaining[0:idx + 1], remaining[idx + 1:]
            packets.append(packet)
        except ValueError:
            return packets


class DVIPProtocol(Protocol):
    def __init__(self, handler):
        super().__init__()
        self.handler = handler

    def connectionMade(self):
        self.handler.log.info('Connected to DVIP device')

    def dataReceived(self, data):
        self.handler.log.debug('<<< {data}', data=data)
        packets = _split_response(data)
        for packet in packets:
            responseType = (packet[1] & 0x70) >> 4
            source = (packet[0] >> 4) - 8

            if source == 1:  # DVIP cameras should always be using VISCA ID 1
                if responseType == 4:
                    self.handler.on_ack()
                elif responseType == 5:
                    if packet[1] & 0x0F == 0:
                        self.handler.on_response(packet[2:-1])
                    else:
                        self.handler.on_complete()
                elif responseType == 6:
                    self.handler.on_error(packet[2])


class DVIPCamera(VISCACameraBase, NetworkDevice):

    default_port = 5002

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_protocol(self):
        return DVIPProtocol(self)

    async def sendVISCA(self, visca, with_lock=None):
        data = [0x81] + visca + [0xFF]
        length = len(data) + 2

        message = [(length >> 8), (length & 0xFF)] + data

        return await self._sendVISCARaw(
            message,
            with_lock
        )

    def send(self, data):
        my_protocol = self.get_protocol()
        if my_protocol and hasattr(my_protocol, 'transport'):
            self.log.debug(f'>>> {data}')
            self.get_protocol().transport.write(data)
        else:
            raise NotConnectedException()
