from avista.core import expose
from avista.serial import SerialDevice
from enum import Enum
from twisted.internet.defer import Deferred, DeferredLock, ensureDeferred
from twisted.internet.protocol import Protocol


DEFAULT_PAN_SPEED = 0x06
DEFAULT_TILT_SPEED = 0x06
DEFAULT_ZOOM_SPEED = 0x06


class VISCAProtocol(Protocol):
    def __init__(self, camera_id, handler):
        super().__init__()
        self.camera_id = camera_id
        self.handler = handler

        self._buffer = []

    def dataReceived(self, data):
        self.handler.log.debug('Serial data: <<< {data}', data=data)

        self._buffer.extend(data)
        if len(self._buffer) > 0 and self._buffer[-1] == 0xFF:
            data = self._buffer

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
            self._buffer.clear()


def constrainPanTiltSpeed(func):
    async def inner(elf, panSpeed=DEFAULT_PAN_SPEED, tiltSpeed=DEFAULT_TILT_SPEED):
        elf.checkPan(panSpeed)
        elf.checkTilt(tiltSpeed)
        await func(elf, panSpeed, tiltSpeed)
    inner.__name__ = func.__name__
    return inner


class VISCACommandsMixin(object):
    MAX_PAN_SPEED = 0x18
    MAX_TILT_SPEED = 0x14
    MIN_ZOOM_SPEED = 0x02
    MAX_ZOOM_SPEED = 0x07
    MAX_PRESETS = 6

    def checkPan(self, pan):
        if pan < 1 or pan > self.maxPanSpeed:
            raise ValueError("Pan speed {} out of range: 1-{}".format(pan, self.maxPanSpeed))

    def checkTilt(self, tilt):
        if tilt < 1 or tilt > self.maxTiltSpeed:
            raise ValueError("Tilt speed {} out of range: 1-{}".format(tilt, self.maxTiltSpeed))

    def checkZoom(self, zoom):
        if zoom < self.minZoomSpeed or zoom > self.maxZoomSpeed:
            raise ValueError("Zoom speed {} out of range: {}-{}".format(zoom, self.minZoomSpeed, self.maxZoomSpeed))

    def checkPreset(self, preset_idx):
        if preset_idx < 0 or preset_idx >= self.maxPresets:
            raise ValueError("Preset {} out of range: 0-{}".format(preset_idx, self.maxPresets - 1))

    @property
    def maxPanSpeed(self):
        return self.MAX_PAN_SPEED

    @property
    def maxTiltSpeed(self):
        return self.MAX_TILT_SPEED

    @property
    def minZoomSpeed(self):
        return self.MIN_ZOOM_SPEED

    @property
    def maxZoomSpeed(self):
        return self.MAX_ZOOM_SPEED

    @property
    def maxPresets(self):
        return self.MAX_PRESETS

    @expose
    @constrainPanTiltSpeed
    async def moveUp(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return await self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x03, 0x01])

    @expose
    @constrainPanTiltSpeed
    async def moveUpLeft(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return await self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x01, 0x01])

    @expose
    @constrainPanTiltSpeed
    async def moveLeft(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return await self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x01, 0x03])

    @expose
    @constrainPanTiltSpeed
    async def moveDownLeft(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return await self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x01, 0x02])

    @expose
    @constrainPanTiltSpeed
    async def moveDown(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return await self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x03, 0x02])

    @expose
    @constrainPanTiltSpeed
    async def moveDownRight(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return await self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x02, 0x02])

    @expose
    @constrainPanTiltSpeed
    async def moveRight(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return await self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x02, 0x03])

    @expose
    @constrainPanTiltSpeed
    async def moveUpRight(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return await self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x02, 0x01])

    @expose
    @constrainPanTiltSpeed
    async def stop(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return await self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x03, 0x03])

    @expose
    async def zoomIn(self, speed=DEFAULT_ZOOM_SPEED):
        self.checkZoom(speed)
        return await self.sendVISCA([0x01, 0x04, 0x07, 0x20 + speed])

    @expose
    async def zoomOut(self, speed=DEFAULT_ZOOM_SPEED):
        self.checkZoom(speed)
        return await self.sendVISCA([0x01, 0x04, 0x07, 0x30 + speed])

    @expose
    async def zoomStop(self, speed):
        return await self.sendVISCA([0x01, 0x04, 0x07, 0x00])

    @expose
    async def focusFar(self):
        await self.focusManual()
        return await self.sendVISCA([0x01, 0x04, 0x08, 0x02])

    @expose
    async def focusNear(self):
        await self.focusManual()
        return await self.sendVISCA([0x01, 0x04, 0x08, 0x03])

    @expose
    async def focusStop(self):
        return await self.sendVISCA([0x01, 0x04, 0x08, 0x00])

    @expose
    async def focusAuto(self):
        return await self.sendVISCA([0x01, 0x04, 0x38, 0x02])

    @expose
    async def focusManual(self):
        return await self.sendVISCA([0x01, 0x04, 0x38, 0x03])

    @expose
    async def focusDirect(self, focus):
        return await self.sendVISCA(
            [
                0x01, 0x04, 0x48,
                (focus & 0xF000) >> 12,
                (focus & 0x0F00) >> 8,
                (focus & 0x00F0) >> 4,
                (focus & 0x000F)
            ]
        )

    @expose
    async def brighter(self):
        await self.sendVISCA([0x01, 0x04, 0x39, 0x0D])  # Put camera into manual exposure mode first!
        return await self.sendVISCA([0x01, 0x04, 0x0D, 0x02])

    @expose
    async def darker(self):
        await self.sendVISCA([0x01, 0x04, 0x39, 0x0D])  # Put camera into manual exposure mode first!
        return await self.sendVISCA([0x01, 0x04, 0x0D, 0x03])

    @expose
    async def autoExposure(self):
        return await self.sendVISCA([0x01, 0x04, 0x39, 0x00])

    @expose
    async def backlightCompOn(self):
        return await self.sendVISCA([0x01, 0x04, 0x33, 0x02])

    @expose
    async def backlightCompOff(self):
        return await self.sendVISCA([0x01, 0x04, 0x33, 0x03])

    @expose
    async def storePreset(self, preset):
        self.checkPreset(preset)
        return await self.sendVISCA([0x01, 0x04, 0x3F, 0x01, preset])

    @expose
    async def recallPreset(self, preset):
        self.checkPreset(preset)
        return await self.sendVISCA([0x01, 0x04, 0x3F, 0x02, preset])

    @expose
    async def whiteBalanceAuto(self):
        return await self.sendVISCA([0x01, 0x04, 0x35, 0x00])

    @expose
    async def whiteBalanceIndoor(self):
        return await self.sendVISCA([0x01, 0x04, 0x35, 0x01])

    @expose
    async def whiteBalanceOutdoor(self):
        return await self.sendVISCA([0x01, 0x04, 0x35, 0x02])

    @expose
    async def whiteBalanceOnePush(self):
        return await self.sendVISCA([0x01, 0x04, 0x35, 0x03])

    @expose
    async def whiteBalanceOnePushTrigger(self):
        return await self.sendVISCA([0x01, 0x04, 0x10, 0x05])

    @expose
    async def setAutoExposure(self):
        return await self.sendVISCA([0x01, 0x04, 0x39, 0x00])

    @expose
    async def setAperturePriority(self):
        return await self.sendVISCA([0x01, 0x04, 0x39, 0x0B])

    @expose
    async def setShutterPriority(self):
        return await self.sendVISCA([0x01, 0x04, 0x39, 0x0A])

    @expose
    async def setManualExposure(self):
        return await self.sendVISCA([0x01, 0x04, 0x39, 0x03])

    @expose
    async def setAperture(self, aperture):
        if isinstance(aperture, CameraSettingEnum):
            av = aperture.code
        else:
            av = aperture
        return await self.sendVISCA([
            0x01, 0x04, 0x4B,
            (av & 0xF000) >> 12,
            (av & 0x0F00) >> 8,
            (av & 0x00F0) >> 4,
            (av & 0x000F)
        ])

    @expose
    async def setShutter(self, shutter):
        if isinstance(shutter, CameraSettingEnum):
            tv = shutter.code
        else:
            tv = shutter
        return await self.sendVISCA([
            0x01, 0x04, 0x4A,
            (tv & 0xF000) >> 12,
            (tv & 0x0F00) >> 8,
            (tv & 0x00F0) >> 4,
            (tv & 0x000F)
        ])

    @expose
    async def setGain(self, gain):
        if isinstance(gain, CameraSettingEnum):
            h = gain.code
        else:
            h = gain
        return await self.sendVISCA([
            0x01, 0x04, 0x4C,
            (h & 0xF000) >> 12,
            (h & 0x0F00) >> 8,
            (h & 0x00F0) >> 4,
            (h & 0x000F)
        ])

    @expose
    async def getZoomPosition(self):
        raw = await self.getVISCA(b'\x09\x04\x47')
        zoom_value = ((raw[0] & 0x0F) << 12) + \
                     ((raw[1] & 0x0F) << 8) + \
                     ((raw[2] & 0x0F) << 4) + \
                     (raw[3] & 0x0F)
        return zoom_value

    @expose
    async def getWhiteBalanceMode(self):
        raw = await self.getVISCA(b'\x09\x04\x35')
        return raw[0]


class VISCACameraBase(VISCACommandsMixin):
    def __init__(self, config):
        super().__init__()
        self._wait_for_ack = config.extra.get('waitForAck', True)
        self._command_lock = DeferredLock()
        self._response_handler = None

    async def _sendVISCARaw(self, visca, with_lock=None):
        if with_lock is None:
            with_lock = self._wait_for_ack
        if with_lock:
            await self._command_lock.acquire()

        if isinstance(visca, list):
            visca = bytes(visca)

        return self._port.writeSomeData(visca)

    async def getVISCA(self, visca):
        if self._wait_for_ack:
            await self._command_lock.acquire()

        response_handler = Deferred()
        self._response_handler = response_handler
        await self.sendVISCA(visca, with_lock=False)

        response = await response_handler
        return response

    def on_ack(self):
        self.log.debug('Ack')
        if self._command_lock.locked:
            self._command_lock.release()

    def on_complete(self):
        self.log.debug('VISCA command execution complete')
        if self._command_lock.locked:
            self._command_lock.release()

    def on_response(self, response_data):
        self.log.debug('Response: {data}', data=response_data)
        if self._response_handler:
            self._response_handler.callback(response_data)
        if self._command_lock.locked:
            self._command_lock.release()

    def on_error(self, error_code):
        self.log.error("VISCA error {error_code}", error_code=error_code)
        if self._command_lock.locked:
            self._command_lock.release()


class SerialVISCACamera(SerialDevice, VISCACameraBase):
    def __init__(self, config):
        self.camera_id = config.extra.get('cameraID', 1)
        super().__init__(config)

    def get_protocol(self):
        return VISCAProtocol(self.camera_id, self)

    async def sendVISCA(self, visca, with_lock=None):
        data = bytes([0x80 + self.camera_id]) + visca + b'\xFF'
        return await self._sendVISCARaw(data, with_lock)


class CameraSettingEnum(Enum):
    def __init__(self, code, label):
        self.code = code
        self.label = label

    @classmethod
    def from_code(cls, code):
        for setting in list(cls):
            if setting.code == code:
                return setting
        return None


class Aperture(CameraSettingEnum):
    CLOSE = (0x00, "Closed")
    F28 = (0x01, "F28")
    F22 = (0x02, "F22")
    F19 = (0x03, "F19")
    F16 = (0x04, "F16")
    F14 = (0x05, "F14")
    F11 = (0x06, "F11")
    F9_6 = (0x07, "F9.6")
    F8 = (0x08, "F8")
    F6_8 = (0x09, "F6.8")
    F5_6 = (0x0A, "F5.6")
    F4_8 = (0x0B, "F4.8")
    F4 = (0x0C, "F4")
    F3_4 = (0x0D, "F3.4")
    F2_8 = (0x0E, "F2.8")
    F2_4 = (0x0F, "F2.4")
    F2 = (0x10, "F2")
    F1_8 = (0x11, "F1.8")


class Shutter(CameraSettingEnum):
    T50 = (0x00, "1/50s")
    T60 = (0x01, "1/60s")
    T75 = (0x02, "1/75s")
    T90 = (0x03, "1/90s")
    T100 = (0x04, "1/100s")
    T120 = (0x05, "1/120s")
    T150 = (0x06, "1/150s")
    T180 = (0x07, "1/180s")
    T215 = (0x08, "1/215s")
    T250 = (0x09, "1/250s")
    T300 = (0x0A, "1/300s")
    T350 = (0x0B, "1/350s")
    T425 = (0x0C, "1/425s")
    T500 = (0x0D, "1/500s")
    T600 = (0x0E, "1/600s")
    T725 = (0x0F, "1/725s")
    T850 = (0x10, "1/850s")
    T1000 = (0x11, "1/1000s")
    T1250 = (0x12, "1/1250s")
    T1500 = (0x13, "1/1500s")
    T1750 = (0x14, "1/1750s")
    T2000 = (0x15, "1/2000s")
    T2500 = (0x16, "1/2500s")
    T3000 = (0x17, "1/3000s")
    T3500 = (0x18, "1/3500s")
    T4000 = (0x19, "1/4000s")
    T6000 = (0x1A, "1/6000s")
    T10000 = (0x1B, "1/10000s")


class Gain(CameraSettingEnum):
    G_MINUS_3 = (0x00, "-3")
    G_0 = (0x01, "0")
    G_3 = (0x02, "3")
    G_6 = (0x03, "6")
    G_9 = (0x04, "9")
    G_12 = (0x05, "12")
    G_15 = (0x06, "15")
    G_18 = (0x07, "18")


class WhiteBalanceMode(CameraSettingEnum):
    AUTO = (0, 'Auto')
    INDOOR = (1, 'Indoor')
    OUTDOOR = (2, 'Outdoor')
    ONE_PUSH = (3, 'One-push')
