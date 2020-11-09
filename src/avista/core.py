from autobahn.twisted.wamp import ApplicationSession
from .constants import Messages, SystemPowerState, Topics, INFRASTRUCTURE_PUBLISH_OPTIONS

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

        await self.subscribe(
            self.on_infrastructure_message,
            Topics.INFRASTRUCTURE
        )

    def publish_infrastructure_message(self, msg_type, data=None):
        self.publish(
            Topics.INFRASTRUCTURE,
            {
                'type': msg_type,
                'data': data
            },
            options=INFRASTRUCTURE_PUBLISH_OPTIONS
        )

    def on_infrastructure_message(self, msg):
        self.log.debug('Infra: {t}', t=msg)
        if msg['type'] == Messages.SYSTEM_POWER_STATE:
            if msg['data'] == SystemPowerState.POWERING_ON:
                self.before_power_on()
            elif msg['data'] == SystemPowerState.POWERED_ON:
                self.after_power_on()
            elif msg['data'] == SystemPowerState.POWERING_OFF:
                self.before_power_off()
            elif msg['data'] == SystemPowerState.POWERED_OFF:
                self.after_power_off()

    # System power event callbacks
    def before_power_on(self):
        pass

    def after_power_on(self):
        pass

    def before_power_off(self):
        pass

    def after_power_off(self):
        pass
