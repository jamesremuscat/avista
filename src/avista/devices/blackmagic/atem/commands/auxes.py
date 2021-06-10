from avista.devices.blackmagic.atem.constants import VideoSource
from construct import Const, Struct, Int8ub, Int16ub, Padding, Default

from .base import BaseCommand, EnumAdapter, clone_state_with_key


class AuxSource(BaseCommand):
    name = b'AuxS'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'source' / EnumAdapter(VideoSource)(Int16ub)
    )

    def apply_to_state(self, state):
        new_state, auxes = clone_state_with_key(state, 'auxes')
        auxes[self.index] = {
            'source': self.source
        }

        return new_state


class SetAuxSource(BaseCommand):
    name = b'CAuS'
    format = Struct(
        Const(1, Int8ub),
        'index' / Int8ub,
        'source' / EnumAdapter(VideoSource)(Default(Int16ub, 0))
    )
