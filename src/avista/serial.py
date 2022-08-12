from avista.core import Device
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.internet.protocol import Protocol


class SerialProtocol(Protocol):
    def dataReceived(self, data):
        print('Serial data: <<< {}'.format(data))


class SerialDevice(Device):
    def __init__(self, config):
        super().__init__(config)
        self._port = config.extra['port']
        self._baudrate = config.extra.get('baudrate', 9600)
        self._connect()

    def _connect(self):
        self.log.info(f'Connecting to serial port {self._port}...')
        self._port = SerialPort(
            self.get_protocol(),
            self._port,
            reactor,
            baudrate=self._baudrate
        )

    def get_protocol(self):
        return SerialProtocol()
