from avista.devices.net import NetworkDevice
from twisted.internet import reactor
from twisted.internet.defer import DeferredLock

from .methods import Audio, Auxes, DSK, MixEffects

from .protocol import ATEMProtocol

import throttle


class ATEM(NetworkDevice, Audio, Auxes, DSK, MixEffects):
    default_port = 9910

    def __init__(self, *args, **kwargs):
        self._state = {}
        self._prev_state = {}
        super(ATEM, self).__init__(*args, **kwargs)
        self._lock = DeferredLock()

    def create_protocol(self):
        return ATEMProtocol(self)

    def _connect(self):
        protocol = self.get_protocol()
        self._connection = reactor.listenUDP(
            self.port,
            protocol
        )

    def send_command(self, command):
        return self.get_protocol().send_command(command)

    def receive_command(self, command):
        self._lock.run(self._receive_command, command)

    def _receive_command(self, command):
        try:
            new_state = command.apply_to_state(self._state)
            if new_state is None:
                self.log.warn('apply_to_state returned None for {}'.format(command.name))

            self._prev_state = self._state
            self._state = new_state

            if new_state.get('state', {}).get('initialized'):
                pass  # print(self._state)

            changed_something = False
            for nsk in new_state.keys():
                if nsk not in self._prev_state or new_state[nsk] is not self._prev_state[nsk]:
                    changed_something = True
                    self.broadcast_device_message(
                        nsk,
                        subtopic=nsk,
                        data=new_state[nsk],
                        retain=True
                    )

            if not changed_something:
                self.log.warn(
                    'Command {cmd} changed... nothing?',
                    cmd=command.__class__.__name__
                )
        except Exception as e:
            self.log.error('Error when applying command {c}: {e}', c=command, e=e)

    @throttle.wrap(0.1, 1)
    def broadcast_device_message(self, msg_type, data=None, subtopic=None, **kwargs):
        return super().broadcast_device_message(msg_type, data, subtopic, **kwargs)
