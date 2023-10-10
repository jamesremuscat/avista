from avista.devices.net import NetworkDevice
from twisted.internet import reactor
from twisted.internet.defer import DeferredLock
from twisted.internet.task import LoopingCall

from .methods import Audio, Auxes, DSK, Macro, MixEffects

from .protocol import ATEMProtocol


class ATEM(NetworkDevice, Audio, Auxes, DSK, Macro, MixEffects):
    default_port = 9910

    def __init__(self, *args, **kwargs):
        self._state = {}
        self._prev_state = {}
        super(ATEM, self).__init__(*args, **kwargs)
        self._lock = DeferredLock()

        self._pending_state_updates = []

    def create_protocol(self):
        return ATEMProtocol(self)

    def _connect(self):
        protocol = self.get_protocol()
        self._connection = reactor.listenUDP(
            self.port,
            protocol
        )

    def create_state_update_loop(self):
        return LoopingCall(
            self._lock.run,
            self._send_updates
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

            for nsk in new_state.keys():
                if nsk not in self._prev_state or new_state[nsk] is not self._prev_state[nsk]:
                    if nsk not in self._pending_state_updates:
                        self._pending_state_updates.append(nsk)

        except Exception as e:
            self.log.error('Error when applying command {c}: {e}', c=command, e=e)

    def _send_updates(self):
        self.log.debug('Sending updates: {updates}', updates=self._pending_state_updates)
        for nsk in self._pending_state_updates:
            self.broadcast_device_message(
                nsk,
                subtopic=nsk,
                data=self._state.get(nsk),
                retain=True
            )
        self._pending_state_updates.clear()
