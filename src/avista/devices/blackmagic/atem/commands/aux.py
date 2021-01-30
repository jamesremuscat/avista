from avista.devices.blackmagic.atem.constants import VideoSource
from construct import Struct, Int8ub, Int16ub, Padding

from .base import BaseCommand, EnumAdapter

import copy


class AuxSource(BaseCommand):
    name = b'AuxS'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'source' / EnumAdapter(VideoSource)(Int16ub)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        new_state.setdefault('auxes', {})[self.index] = {
            'source': self.source
        }

        return new_state
