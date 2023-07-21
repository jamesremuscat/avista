from avista.core import Device, expose
from twisted.internet.defer import Deferred
from twisted.internet import reactor


def pause(secs):
    d = Deferred()
    reactor.callLater(secs, d.callback, None)
    return d


class BlindsArray(Device):
    def __init__(self, config):
        super().__init__(config)
        self.blinds = config.extra['blinds']  # Should be an array of blind definitions
        # A blind definition is an object of the form:
        # {
        #   "up": ["device_name", channelNumber],
        #   "down": ["device_name", channelNumber],
        #   "stop": ["device_name", channelNumber],
        # }
        self.pulse = config.extra.get('pulse', False)

    async def blindAction(self, action, index):
        if index < len(self.blinds):
            blind = self.blinds[index]
            if action in blind:
                relays = blind[action]
                if self.pulse:
                    self.log.info('Pulsing blind index {idx}', idx=index)
                    await self.safe_call(f'{relays[0]}.pulseOn', relays[1])
                    await pause(0.25)
                else:
                    self.log.info('Toggling blind index {idx}', idx=index)
                    await self.safe_call(f'{relays[0]}.turnOn', relays[1])
                    await pause(0.5)
                    await self.safe_call(f'{relays[0]}.turnOff', relays[1])

    @expose
    async def raiseUp(self, index):
        return await self.blindAction('up', index)

    @expose
    async def raiseAll(self):
        for blind in range(len(self.blinds)):
            await self.raiseUp(blind)

    @expose
    async def lower(self, index):
        return await self.blindAction('down', index)

    @expose
    async def lowerAll(self):
        for blind in range(len(self.blinds)):
            await self.lower(blind)

    @expose
    async def stop(self, index):
        return await self.blindAction('stop', index)

    @expose
    async def stopAll(self):
        for blind in range(len(self.blinds)):
            await self.stop(blind)
