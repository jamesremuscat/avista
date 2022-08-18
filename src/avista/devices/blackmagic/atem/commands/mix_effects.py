from avista.devices.blackmagic.atem.constants import KeyType, PatternStyle, TransitionStyle, VideoSource
from construct import BitStruct, Const, Struct, Int8ub, Int16ub, Int16sb, Padding, Flag, Rebuild, obj_, Default

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
        'source' / EnumAdapter(VideoSource)(Default(Int16ub, 0))
    )


class SetProgramInput(BaseCommand):
    name = b'CPgI'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'source' / EnumAdapter(VideoSource)(Default(Int16ub, 0))
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
    Padding(3),
    'key_4' / Default(Flag, False),
    'key_3' / Default(Flag, False),
    'key_2' / Default(Flag, False),
    'key_1' / Default(Flag, False),
    'background' / Default(Flag, False),
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
    Padding(6),
    'next' / Flag,
    'style' / Flag,
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
        'style' / EnumAdapter(TransitionStyle)(Default(Int8ub, 0)),
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


class SetTransitionPosition(BaseSetCommand):
    name = b'CTPs'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'position' / Int16ub
    )


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


class SetTransitionMixProperties(BaseSetCommand):
    name = b'CTMx'
    format = Struct(
        'index' / Int8ub,
        'rate' / Int8ub,
        Padding(2)  # This might need to be magic: 0x93, 0x07?
    )


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


class SetTransitionDipProperties(BaseSetCommand):
    class Mask:
        format = BitStruct(
            'rate' / Flag,
            'source' / Flag,
            Padding(6)
        )

        @classmethod
        def calculate(cls, obj):
            return cls.format.parse(
                cls.format.build(
                    dict(
                        rate=hasattr(obj, 'rate'),
                        source=hasattr(obj, 'source')
                    )
                )
            )

    name = b'CTDp'
    format = Struct(
        'mask' / Rebuild(Mask.format, Mask.calculate),
        'index' / Int8ub,
        'rate' / Default(Int8ub, 0),
        Padding(1),
        'source' / EnumAdapter(VideoSource)(Default(Int16ub, 0)),
        Padding(1)
    )


class TransitionWipeProperties(BaseCommand):
    name = b'TWpP'
    format = Struct(
        'index' / Int8ub,
        'rate' / Int8ub,
        'pattern' / EnumAdapter(PatternStyle)(Int8ub),
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


class TransitionDVEProperties(BaseCommand):
    name = b'TDvP'
    format = Struct(
        'index' / Int8ub,
        'rate' / Int8ub,
        Padding(1),
        'style' / Int8ub,
        'fill_source' / EnumAdapter(VideoSource)(Int16ub),
        'key_source' / EnumAdapter(VideoSource)(Int16ub),
        'enable_key' / Flag,
        'pre_multiplied' / Flag,
        'clip' / Int16ub,
        'gain' / Int16ub,
        'invert' / Flag,
        'reverse' / Flag,
        'flip_flop' / Flag,
        Padding(2)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me.setdefault('transition', {}).setdefault('properties', {})['dve'] = {
            'rate': self.rate,
            'style': self.style,
            'fill_source': self.fill_source,
            'key_source': self.key_source,
            'enable_key': self.enable_key,
            'pre_multiplied': self.pre_multiplied,
            'clip': self.clip,
            'gain': self.gain,
            'invert': self.invert,
            'reverse': self.reverse,
            'flip_flop': self.flip_flop
        }
        return new_state


class TransitionStingerProperties(BaseCommand):
    name = b'TStP'
    format = Struct(
        'index' / Int8ub,
        'source' / Int8ub,
        'pre_multiplied' / Flag,
        Padding(1),
        'clip' / Int16ub,
        'gain' / Int16ub,
        'invert' / Flag,
        Padding(1),
        'pre_roll' / Int16ub,
        'duration' / Int16ub,
        'trigger_point' / Int16ub,
        'mix_rate' / Int16ub,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        me.setdefault('transition', {}).setdefault('properties', {})['stinger'] = {
            'source': self.source,
            'pre_multiplied': self.pre_multiplied,
            'clip': self.clip,
            'gain': self.gain,
            'invert': self.invert,
            'pre_roll': self.pre_roll,
            'duration': self.duration,
            'trigger_point': self.trigger_point,
            'mix_rate': self.mix_rate
        }
        return new_state


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


class SetKeyerOnAir(BaseSetCommand):
    name = b'CKOn'
    format = Struct(
        'index' / Int8ub,
        'key_index' / Int8ub,
        'enabled' / Flag,
        Padding(1)
    )


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


class SetKeyerType(BaseSetCommand):
    class Mask:
        format = BitStruct(
            'type' / Flag,
            'fly_enabled' / Flag,
            Padding(6)

        )

        @classmethod
        def calculate(cls, obj):
            return cls.format.parse(
                cls.format.build(
                    dict(
                        type=hasattr(obj, 'type'),
                        fly_enabled=hasattr(obj, 'fly_enabled')
                    )
                )
            )

    name = b'CKTp'
    format = Struct(
        'mask' / Rebuild(Mask.format, Mask.calculate),
        'index' / Int8ub,
        'key_index' / Int8ub,
        'type' / EnumAdapter(KeyType)(Default(Int8ub, 0)),
        'fly_enabled' / Default(Flag, False),
        Padding(3)
    )


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


class KeyPatternProperties(BaseCommand):
    name = b'KePt'
    format = Struct(
        'index' / Int8ub,
        'key_index' / Int8ub,
        'pattern' / EnumAdapter(PatternStyle)(Int8ub),
        Padding(1),
        'size' / Int16ub,
        'symmetry' / Int16ub,
        'softness' / Int16ub,
        'position_x' / Int16ub,
        'position_y' / Int16ub,
        'invert' / Flag,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        keyer = me.setdefault('keyers', {}).get(self.key_index, {})

        me['keyers'][self.key_index] = copy.copy(keyer)
        me['keyers'][self.key_index]['pattern'] = {
            'pattern': self.pattern,
            'size': self.size,
            'symmetry': self.symmetry,
            'softness': self.softness,
            'invert': self.invert,
            'position': {
                'x': self.position_x,
                'y': self.position_y
            }
        }

        return new_state

# TODO: DVE, fly, fly frame


class FadeToBlackProperties(BaseCommand):
    name = b'FtbP'
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
    name = b'FtbS'
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


class SetFadeToBlackRate(BaseSetCommand):
    name = b'FtbC'
    format = Struct(
        'mask' / Const(1),
        'index' / Int8ub,
        'rate' / Int8ub,
        Padding(1)
    )


class ToggleFadeToBlack(BaseSetCommand):
    name = b'FtbA'
    format = Struct(
        'index' / Int8ub,
        Padding(3)
    )


class ColorGeneratorState(BaseCommand):
    name = b'ColV'
    format = Struct(
        'index' / Int8ub,
        Padding(1),
        'hue' / Int16ub,
        'saturation' / Int16ub,
        'luma' / Int16ub
    )

    def apply_to_state(self, state):
        new_state, mes = clone_state_with_key(state, 'mes')

        me = mes.setdefault(self.index, {})
        cg = me.setdefault('color_generators', {}).setdefault(self.index, {})
        cg['state'] = {
            'hue': self.hue,
            'saturation': self.saturation,
            'luma': self.luma
        }

        return new_state
