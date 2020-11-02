from autobahn.twisted.wamp import ApplicationSession

import inspect


def expose(func):
    setattr(func, '__exposed__', True)
    return func


class Device(ApplicationSession):
    def __init__(self, config):
        super().__init__(config)
        self.name = config.extra['name']

    async def onJoin(self, details):
        for name, attr in inspect.getmembers(self):
            if inspect.ismethod(attr):
                if getattr(attr, '__exposed__', False):
                    uri = '{}.{}'.format(
                        self.name,
                        name
                    )
                    await self.register(attr, uri)
                    self.log.info('Registered {uri}', uri=uri)
