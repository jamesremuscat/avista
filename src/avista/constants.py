from autobahn.wamp.types import PublishOptions


class SystemPowerState(object):
    POWERED_OFF = 'off'
    POWERING_ON = 'turning_on'
    POWERING_OFF = 'turning_off'
    POWERED_ON = 'on'


class Messages(object):
    SYSTEM_POWER_STATE = 'avista.infrastructure.SystemPowerState'


class Topics(object):
    INFRASTRUCTURE = 'avista.infrastructure'


INFRASTRUCTURE_PUBLISH_OPTIONS = PublishOptions(
    exclude_me=False,
    retain=True
)
