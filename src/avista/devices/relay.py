from avista.core import expose
from avista.serial import SerialDevice
from twisted.internet import reactor
from twisted.internet.protocol import Protocol


class ICStationProtocol(Protocol):
    def __init__(self, card_device):
        self._card_device = card_device

    def send_init_message(self):
        self._card_device._port.writeSomeData(b'\x50')
        reactor.callLater(0.1, self.finish_init)

    def finish_init(self):
        self._card_device._port.writeSomeData(b'\x51')
        reactor.callLater(0.1, self._card_device._send_state_byte)

    def dataReceived(self, data):
        if data == 0xAB:
            channels = 4
        elif data == 0xAC:
            channels = 8
        elif data == 0xAD:
            channels = 2
        else:
            channels = None

        if channels:
            self._card_device.set_channel_count(channels)


class ICStationRelayCard(SerialDevice):
    def __init__(self, config):
        super().__init__(config)
        self.set_channel_count(8, send=False)
        self.protocol.send_init_message()

    def get_protocol(self):
        self.protocol = ICStationProtocol(self)
        return self.protocol

    def set_channel_count(self, channels, send=True):
        self.log.info('Setting channel count: {channels}', channels=channels)
        self._state = [False for _ in range(channels)]  # True = on, False = off
        if send:
            self._send_state_byte()

    @expose
    def turnOn(self, channel):
        if 0 < channel <= len(self._state):
            self._state[channel - 1] = True
            self._send_state_byte()

    @expose
    def turnOff(self, channel):
        if 0 < channel <= len(self._state):
            self._state[channel - 1] = False
            self._send_state_byte()

    def _send_state_byte(self):
        stateByte = 0x0
        for i in range(0, len(self._state)):
            if not self._state[i]:  # Card requires bit = 0 to turn relay on
                stateByte += 1 << i
        self._port.writeSomeData(bytes([stateByte]))


class KMtronicRelayCard(SerialDevice):
    @expose
    def turnOn(self, channel):
        self._port.writeSomeData(bytes([0xFF, channel, 0x01]))

    @expose
    def turnOff(self, channel):
        self._port.writeSomeData(bytes([0xFF, channel, 0x00]))
