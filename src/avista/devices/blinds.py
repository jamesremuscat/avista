from avista.core import Device, expose
from twisted.internet import reactor


class BlindsArray(Device):
    def __init__(self, config):
        super().__init__(config)
        self.blinds = config.extra['blinds']

    async def blindAction(self, action, index):
        if index in self.blinds:
            blind = self.blinds[index]
            if action in blind:
                relays = blind[action]
                self.safe_call(f'{relays[0]}.turnOn', relays[1])
                reactor.callLater(0.5, self.safe_call, f'{relays[0]}.turnOff', relays[1])

    @expose
    async def raiseUp(self, index):
        return await self.blindAction('up', index)

    @expose
    async def raiseAll(self):
        for blind in self.blinds.keys():
            self.raiseUp(blind)

    @expose
    async def lower(self, index):
        return await self.blindAction('down', index)

    @expose
    async def lowerAll(self):
        for blind in self.blinds.keys():
            self.lower(blind)

    @expose
    async def stop(self, index):
        return await self.blindAction('stop', index)

    @expose
    async def stopAll(self):
        for blind in self.blinds.keys():
            self.stop(blind)
