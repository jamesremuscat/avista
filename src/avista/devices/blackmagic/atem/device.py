from avista.core import expose
from avista.devices.net import NetworkDevice
from twisted.internet import reactor

from .commands.mix_effects import SetProgramInput
from .constants import VideoSource
from .protocol import ATEMProtocol


class ATEM(NetworkDevice):
    default_port = 9910

    def __init__(self, *args, **kwargs):
        self._state = {}
        self._prev_state = {}
        super(ATEM, self).__init__(*args, **kwargs)

    def create_protocol(self):
        return ATEMProtocol(self)

    def _connect(self):
        protocol = self.get_protocol()
        self._connection = reactor.listenUDP(
            self.port,
            protocol
        )

    def before_power_off(self):
        if not self.always_powered:
            if self._connection:
                self._connection.stopListening()
            self.protocol = None

    def receive_command(self, command):
        new_state = command.apply_to_state(self._state)

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

    @expose
    def set_program_input(self, input, me=0):
        cmd = SetProgramInput(source=VideoSource(input), index=me)
        self.get_protocol().send_command(cmd)
