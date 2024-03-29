from avista.core import Device, expose
from avista.constants import SystemPowerState, Messages
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredLock


def sleep(secs):
    d = Deferred()
    reactor.callLater(secs, d.callback, None)
    return d


class StaggeredSystemPower(Device):
    def __init__(self, config):
        super().__init__(config)

        self._switches = config.extra.get('switches', [])
        self._delay = config.extra.get('delay', 3)
        self._state = SystemPowerState.POWERED_OFF

        # Use a lock to prevent trying to power off while we're in the
        # middle of a power-on sequence.
        self._lock = DeferredLock()

    async def onJoin(self, details):
        await super().onJoin(details)
        self._set_state(self._state)

    @expose
    async def power_on(self):
        await self._lock.acquire()
        self.log.info('Turning system power on')
        self._set_state(SystemPowerState.POWERING_ON)
        for device, switch in self._switches:
            await self.safe_call('{}.turnOn'.format(device), switch)
            await sleep(self._delay)
        self._set_state(SystemPowerState.POWERED_ON)
        self.log.info('System powered on')
        self._lock.release()

    @expose
    async def power_off(self):
        await self._lock.acquire()
        self.log.info('Turning system power off')
        self._set_state(SystemPowerState.POWERING_OFF)
        for device, switch in reversed(self._switches):
            await self.safe_call('{}.turnOff'.format(device), switch)
            await sleep(self._delay)
        self._set_state(SystemPowerState.POWERED_OFF)
        self.log.info('System power turned off')
        self._lock.release()

    def _set_state(self, state):
        self._state = state
        self.broadcast_infrastructure_message(
            Messages.SYSTEM_POWER_STATE,
            self._state,
            retain=True
        )
        self.broadcast_device_message(
            Messages.SYSTEM_POWER_STATE,
            self._state,
            retain=True
        )

    def on_infrastructure_message(self, message):
        if message['type'] == Messages.REGISTER_DEVICE:
            # Rebroadcast our new state so the new device picks up on it
            self._set_state(self._state)
