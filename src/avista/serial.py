from avista.core import Device
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.internet.protocol import Protocol


class SerialProtocol(Protocol):
    def dataReceived(self, data):
        print('Serial data: <<< {}'.format(data))


class SerialDevice(Device):
    protocol = SerialProtocol()

    def __init__(self, config):
        super().__init__(config)

        self._port = SerialPort(
            self.get_protocol(),
            config.extra['port'],
            reactor,
            baudrate=config.extra.get('baudrate', 9600)
        )

    def get_protocol(self):
        return SerialProtocol()
