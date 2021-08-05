from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.types import PublishOptions, SubscribeOptions
from twisted.internet import reactor
from twisted.internet.defer import ensureDeferred
from twisted.internet.task import LoopingCall
from .constants import Messages, SystemPowerState, Topics, INFRASTRUCTURE_PUBLISH_OPTIONS

import inspect


def expose(func):
    setattr(func, '__exposed__', True)
    return func


def map_function_spec(func):
    spec = inspect.getargspec(func)
    return {
        'args': spec.args[1:],  # Filter out 'self'
        'varargs': spec.varargs,
        'keywords': spec.keywords,
        'defaults': spec.defaults,
        'doc': func.__doc__.strip() if func.__doc__ else None
    }


class Device(ApplicationSession):
    def __init__(self, config):
        super().__init__(config)
        self.name = config.extra['name']

    async def onJoin(self, details):

        for method in self._get_exposed_methods():
            uri = '{}.{}'.format(
                self.name,
                method.__name__
            )
            await self.register(method, uri)
            self.log.info('Registered {uri}', uri=uri)

        await self.subscribe(
            self.on_infrastructure_message,
            '()/{}'.format(Topics.INFRASTRUCTURE, Messages.SYSTEM_POWER_STATE),
            SubscribeOptions(
                get_retained=True
            )
        )

        await self.subscribe(
            self.on_infrastructure_message,
            Topics.INFRASTRUCTURE,
            SubscribeOptions(
                match='prefix',
                get_retained=True
            )
        )

        self._broadcast_registration()

    def _get_exposed_methods(self):
        methods = []
        for name, attr in inspect.getmembers(self):
            if inspect.ismethod(attr):
                if getattr(attr, '__exposed__', False):
                    methods.append(attr)
        return methods

    def _broadcast_registration(self):
        self.publish(
            Topics.INFRASTRUCTURE,
            {
                'type': Messages.REGISTER_DEVICE,
                'data': {
                    'name': self.name,
                    'methods': {
                        m.__name__: map_function_spec(m) for m in self._get_exposed_methods() if m.__name__[0] != '_'
                    }
                }
            }
        )

    def broadcast_infrastructure_message(self, msg_type, data=None, **kwargs):
        self.publish(
            '{}/{}'.format(
                Topics.INFRASTRUCTURE,
                msg_type
            ),
            {
                'type': msg_type,
                'data': data
            },
            options=PublishOptions(**kwargs)
        )

    def publish(self, topic, payload, **kwargs):
        self.log.debug(
            'Publishing to {topic}: {payload}',
            topic=topic,
            payload=payload
        )
        super().publish(topic, payload, **kwargs)

    @property
    def broadcast_topic(self):
        return 'avista.devices.{}'.format(self.name)

    def broadcast_device_message(self, msg_type, data=None, subtopic=None, **kwargs):
        self.publish(
            '{}/{}'.format(self.broadcast_topic, subtopic) if subtopic else self.broadcast_topic,
            {
                'type': msg_type,
                'data': data
            },
            options=PublishOptions(**kwargs)
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
        elif msg['type'] == Messages.RE_REGISTER_ALL_DEVICES:
            self._broadcast_registration()

    # System power event callbacks
    def before_power_on(self):
        pass

    def after_power_on(self):
        pass

    def before_power_off(self):
        pass

    def after_power_off(self):
        pass

    # Wraps `.call` in a try/except to neutralise and log Autobahn errors.
    async def safe_call(self, method, *args, **kwargs):
        try:
            await self.call(method, *args, **kwargs)
        except ApplicationError as e:
            self.log.warn('Unable to call method {method}: {err}', method=method, err=e.error)

    @expose
    def _liveness_check(self):
        return True


class DeviceManager(Device):
    def __init__(self, config):
        config.extra['name'] = 'DeviceManager'
        super().__init__(config)
        self.devices = {}
        self._update_required = False
        self._update_task = None

    async def onJoin(self, details):
        await super().onJoin(details)
        self.broadcast_infrastructure_message(Messages.RE_REGISTER_ALL_DEVICES)

        self._update_task = LoopingCall(
            lambda: ensureDeferred(self._maybe_publish_manifest())
        )
        self._update_task.start(5)

    def onLeave(self, details):
        if self._update_task:
            self._update_task.stop()

    async def _maybe_publish_manifest(self):
        # Check liveness of all our registered devices
        for device_name in list(self.devices.keys()):
            try:
                result = await self.call('{}._liveness_check'.format(device_name))
                if result is False:
                    del self.devices[device_name]
                    self._update_required = True
            except ApplicationError:
                del self.devices[device_name]
                self._update_required = True

        # If necessary, publish an updated manifest
        if self._update_required:
            self.publish_device_manifest()
            self._update_required = False

    def publish_device_manifest(self):
        self.broadcast_infrastructure_message(
            Messages.DEVICE_LISTING,
            self.devices,
            retain=True
        )

    def on_infrastructure_message(self, message):
        if message['type'] == Messages.REGISTER_DEVICE:
            registration = message['data']
            self.devices[registration['name']] = registration['methods']
            self._update_required = True
