from avista.devices.blackmagic.atem.constants import KeyType, TransitionStyle, VideoSource
from construct import BitStruct, Struct, Int8ub, Int16ub, Int16sb, Padding, Flag, Rebuild, obj_, Default

from .base import BaseCommand, BaseSetCommand, EnumAdapter, EnumFlagAdapter, clone_state_with_key, recalculate_synthetic_tally

import copy


class PreviewInput(BaseCommand):
    name = b'PrvI'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'source' / EnumAdapter(VideoSource)(Int16ub),
        Padding(4)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me['preview'] = self.source
        return recalculate_synthetic_tally(new_state)


class SetPreviewInput(BaseCommand):
    name = b'CPvI'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'source' / EnumAdapter(VideoSource)(Int16ub)
    )


class SetProgramInput(BaseCommand):
    name = b'CPgI'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'source' / EnumAdapter(VideoSource)(Int16ub)
    )


class ProgramInput(BaseCommand):
    name = b'PrgI'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'source' / EnumAdapter(VideoSource)(Int16ub)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me['program'] = self.source
        return recalculate_synthetic_tally(new_state)


class PerformCut(BaseCommand):
    name = b'DCut'
    format = Struct(
        'index' / Int8ub,
        Padding(3)
    )


class PerformAuto(BaseCommand):
    name = b'DAut'
    format = Struct(
        'index' / Int8ub,
        Padding(3)
    )


TransitionSelectionField = BitStruct(
    'background' / Default(Flag, False),
    'key_1' / Default(Flag, False),
    'key_2' / Default(Flag, False),
    'key_3' / Default(Flag, False),
    'key_4' / Default(Flag, False),
    Padding(3)
)


class TransitionProperties(BaseCommand):
    name = b'TrSS'
    format = Struct(
        'index' / Int8ub,
        'style' / EnumAdapter(TransitionStyle)(Int8ub),
        'next_transition' / TransitionSelectionField,
        'style_next' / EnumAdapter(TransitionStyle)(Int8ub),
        'next_transition_next' / TransitionSelectionField,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me['transition'] = {
            'style': self.style,
            'next': {
                'background': self.next_transition.background,
                'key_1': self.next_transition.key_1,
                'key_2': self.next_transition.key_2,
                'key_3': self.next_transition.key_3,
                'key_4': self.next_transition.key_4,
            },
            'style_next': self.style_next,
            'next_transition': {
                'background': self.next_transition_next.background,
                'key_1': self.next_transition_next.key_1,
                'key_2': self.next_transition_next.key_2,
                'key_3': self.next_transition_next.key_3,
                'key_4': self.next_transition_next.key_4,
            },
        }
        return new_state


CTTp_mask = BitStruct(
    'style' / Flag,
    'next' / Flag,
    Padding(6)
)


def _calculate_CTTp_mask(stp):
    return CTTp_mask.parse(
        CTTp_mask.build(
            dict(
                style=hasattr(stp, 'style'),
                next=hasattr(stp, 'next')
            )
        )
    )


class SetTransitionProperties(BaseSetCommand):
    name = b'CTTp'
    format = Struct(
        'mask' / Rebuild(CTTp_mask, lambda obj: _calculate_CTTp_mask(obj)),
        'index' / Int8ub,
        'style' / Default(EnumAdapter(TransitionStyle)(Int8ub), 0),
        'next' / TransitionSelectionField
    )


class TransitionPreview(BaseCommand):
    name = b'TrPr'
    format = Struct(
        'index' / Int8ub,
        'enabled' / Flag,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me.setdefault('transition', {})['preview'] = self.enabled
        return new_state


class TransitionPosition(BaseCommand):
    name = b'TrPs'
    format = Struct(
        'index' / Int8ub,
        'in_transition' / Flag,
        'frames_remaining' / Int8ub,
        Padding(1),
        'position' / Int16ub,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me.setdefault('transition', {})['position'] = {
            'in_transition': self.in_transition,
            'frames_remaining': self.frames_remaining,
            'position': self.position
        }
        return recalculate_synthetic_tally(new_state)


class TransitionMixProperties(BaseCommand):
    name = b'TMxP'
    format = Struct(
        'index' / Int8ub,
        'rate' / Int8ub,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me.setdefault('transition', {}).setdefault('properties', {})['mix'] = {
            'rate': self.rate
        }
        return new_state


class TransitionDipProperties(BaseCommand):
    name = b'TDpP'
    format = Struct(
        'index' / Int8ub,
        'rate' / Int8ub,
        'source' / EnumAdapter(VideoSource)(Int16ub)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me.setdefault('transition', {}).setdefault('properties', {})['dip'] = {
            'rate': self.rate,
            'source': self.source
        }
        return new_state


class TransitionWipeProperties(BaseCommand):
    name = b'TWpB'
    format = Struct(
        'index' / Int8ub,
        'rate' / Int8ub,
        'pattern' / Int8ub,
        Padding(1),
        'width' / Int16ub,
        'fill_source' / EnumAdapter(VideoSource)(Int16ub),
        'symmetry' / Int16ub,
        'softness' / Int16ub,
        'position_x' / Int16ub,
        'position_y' / Int16ub,
        'reverse' / Flag,
        'flip_flop' / Flag
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me.setdefault('transition', {}).setdefault('properties', {})['wipe'] = {
            'rate': self.rate,
            'pattern': self.pattern,
            'width': self.width,
            'fill_source': self.fill_source,
            'symmetry': self.symmetry,
            'softness': self.softness,
            'position': {
                'x': self.position_x,
                'y': self.position_y
            },
            'reverse': self.reverse,
            'flip_flop': self.flip_flop
        }
        return new_state

# TODO stinger, DVE transition properties


class KeyerOnAir(BaseCommand):
    name = b'KeOn'
    format = Struct(
        'index' / Int8ub,
        'key_index' / Int8ub,
        'enabled' / Flag,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        keyer = me.setdefault('keyers', {}).get(self.key_index, {})

        me['keyers'][self.key_index] = copy.copy(keyer)
        me['keyers'][self.key_index]['on_air'] = self.enabled

        return new_state


class KeyerBaseProperties(BaseCommand):
    name = b'KeBP'
    format = Struct(
        'index' / Int8ub,
        'key_index' / Int8ub,
        'type' / EnumAdapter(KeyType)(Int8ub),
        Padding(1),
        'can_fly' / Flag,
        'fly_enabled' / Flag,
        'fill_source' / EnumAdapter(VideoSource)(Int16ub),
        'key_source' / EnumAdapter(VideoSource)(Int16ub),
        'mask_enabled' / Flag,
        Padding(1),
        'mask_top' / Int16sb,
        'mask_bottom' / Int16sb,
        'mask_left' / Int16sb,
        'mask_right' / Int16sb,
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        keyer = me.setdefault('keyers', {}).get(self.key_index, {})

        me['keyers'][self.key_index] = copy.copy(keyer)
        me['keyers'][self.key_index]['type'] = self.type
        me['keyers'][self.key_index]['can_fly'] = self.can_fly
        me['keyers'][self.key_index]['fly_enabled'] = self.fly_enabled
        me['keyers'][self.key_index]['fill_source'] = self.fill_source
        me['keyers'][self.key_index]['key_source'] = self.key_source
        me['keyers'][self.key_index]['mask'] = {
            'enabled': self.mask_enabled,
            'top': self.mask_top,
            'bottom': self.mask_bottom,
            'left': self.mask_left,
            'right': self.mask_right
        }

        return new_state


class KeyLumaProperties(BaseCommand):
    name = b'KeLm'
    format = Struct(
        'index' / Int8ub,
        'key_index' / Int8ub,
        'pre_multiplied' / Flag,
        Padding(1),
        'clip' / Int16ub,
        'gain' / Int16ub,
        'invert' / Flag,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        keyer = me.setdefault('keyers', {}).get(self.key_index, {})

        me['keyers'][self.key_index] = copy.copy(keyer)
        me['keyers'][self.key_index]['luma'] = {
            'pre_multiplied': self.pre_multiplied,
            'clip': self.clip,
            'gain': self.gain,
            'invert': self.invert
        }

        return new_state


class KeyChromaProperties(BaseCommand):
    name = b'KeCk'
    format = Struct(
        'index' / Int8ub,
        'key_index' / Int8ub,
        'hue' / Int16ub,
        'gain' / Int16ub,
        'y_suppress' / Int16ub,
        'lift' / Int16ub,
        'narrow' / Flag,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        keyer = me.setdefault('keyers', {}).get(self.key_index, {})

        me['keyers'][self.key_index] = copy.copy(keyer)
        me['keyers'][self.key_index]['chroma'] = {
            'hue': self.hue,
            'gain': self.gain,
            'y-suppress': self.y_suppress,
            'lift': self.lift,
            'narrow': self.narrow
        }

        return new_state

# TODO: Pattern, DVE, fly, fly frame


class FadeToBlackProperties(BaseCommand):
    name = b'FtBP'
    format = Struct(
        'index' / Int8ub,
        'rate' / Int8ub,
        Padding(2)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        ftb = me.setdefault('fade_to_black', {})
        ftb['rate'] = self.rate

        return new_state


class FadeToBlackState(BaseCommand):
    name = b'FtBS'
    format = Struct(
        'index' / Int8ub,
        'fully_black' / Flag,
        'in_transition' / Flag,
        'frames_remaining' / Int8ub
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        ftb = me.setdefault('fade_to_black', {})
        ftb['state'] = {
            'fully_black': self.fully_black,
            'in_transition': self.in_transition,
            'frames_remaining': self.frames_remaining
        }

        return new_state
