from autobahn.twisted.wamp import ApplicationSession
from twisted.internet import reactor
from twisted.internet.defer import DeferredLock, inlineCallbacks
from twisted.internet.serialport import SerialPort
from twisted.internet.protocol import Protocol, Factory


class SerialProtocol(Protocol):
    def dataReceived(self, data):
        print('Serial data: <<< {}'.format(data))


class SerialDevice(ApplicationSession):
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


class VISCAProtocol(Protocol):
    def __init__(self, camera_id, handler):
        super().__init__()
        self.camera_id = camera_id
        self.handler = handler

    def dataReceived(self, data):
        print('Serial data: <<< {}'.format(data))
        responseType = (data[1] & 0x70) >> 4
        source = (data[0] >> 4) - 8

        if source == self.camera_id:
            if responseType == 4:
                self.handler.on_ack()
            elif responseType == 5:
                if data[1] & 0x0F == 0:
                    self.handler.on_response(data[2:-1])
                else:
                    self.handler.on_complete()
            elif responseType == 6:
                self.handler.on_error(data[2])


class VISCACamera(SerialDevice):

    def __init__(self, config):
        self.camera_id = config.extra.get('cameraID', 1)
        super().__init__(config)
        self._wait_for_ack = config.extra.get('waitForAck', True)
        self._command_lock = DeferredLock()

    def get_protocol(self):
        return VISCAProtocol(self.camera_id, self)

    def on_ack(self):
        print('Ack')
        if self._command_lock.locked:
            self._command_lock.release()

    def on_complete(self):
        print('Complete')

    def on_response(self, response_data):
        print('Response: {}'.format(response_data))
        if self._command_lock.locked:
            self._command_lock.release()

    def on_error(self, error_code):
        print("Error {}".format(error_code))

    async def sendVISCA(self, visca):
        if self._wait_for_ack:
            await self._command_lock.acquire()
            print('Got lock')

        data = bytes([0x80 + self.camera_id]) + visca + b'\xFF'
        self._port.writeSomeData(
            data
        )
        print('Wrote data {}'.format(data))

    async def onJoin(self, details):
        await self.sendVISCA(b'\x01\x07\x01\x02')
        print('Sent stuff')
