from avista.devices.blackmagic.atem.constants import KeyType, VideoSource
from construct import Struct, Int8ub, Int16ub, Int16sb, Padding, Flag

from .base import BaseCommand, EnumAdapter, EnumFlagAdapter

import copy


class DownstreamKeyerSource(BaseCommand):
    name = b'DskB'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'fill_source' / EnumAdapter(VideoSource)(Int16ub),
        'key_source' / EnumAdapter(VideoSource)(Int16ub),
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        dsk = copy.copy(new_state.setdefault('dsks', {}).get(self.index, {}))

        dsk['fill_source'] = self.fill_source
        dsk['key_source'] = self.key_source

        new_state['dsks'][self.index] = dsk

        return new_state


class DownstreamKeyerProperties(BaseCommand):
    name = b'DskP'
    format = Struct(
        'index' / Int8ub,
        'tie' / Flag,
        'rate' / Int8ub,
        'pre_multiplied' / Flag,
        'clip' / Int16ub,
        'gain' / Int16ub,
        'invert' / Flag,
        'mask' / Flag,
        'mask_top' / Int16sb,
        'mask_bottom' / Int16sb,
        'mask_left' / Int16sb,
        'mask_right' / Int16sb,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        dsk = copy.copy(new_state.setdefault('dsks', {}).get(self.index, {}))

        dsk['tie'] = self.tie
        dsk['rate'] = self.rate
        dsk['pre_multiplied'] = self.pre_multiplied
        dsk['clip'] = self.clip
        dsk['gain'] = self.gain
        dsk['invert'] = self.invert
        dsk['mask'] = {
            'enabled': self.mask,
            'top': self.mask_top,
            'bottom': self.mask_bottom,
            'left': self.mask_left,
            'right': self.mask_right
        }

        new_state['dsks'][self.index] = dsk

        return new_state


class DownstreamKeyerState(BaseCommand):
    name = b'DskS'
    format = Struct(
        'index' / Int8ub,
        'on_air' / Flag,
        'is_transitioning' / Flag,
        'is_auto_transitioning' / Flag,
        'frames_remaining' / Int8ub,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        dsk = copy.copy(new_state.setdefault('dsks', {}).get(self.index, {}))

        dsk['state'] = {
            'on_air': self.on_air,
            'is_transitioning': self.is_transitioning,
            'is_auto_transitioning': self.is_auto_transitioning,
            'frames_remaining': self.frames_remaining
        }

        new_state['dsks'][self.index] = dsk

        return new_state
