from avista.devices.blackmagic.atem.constants import BevelType, VideoSource
from construct import BitStruct, Struct, Default, Int8ub, Int16ub, Int16sb, Padding, Flag, Rebuild

from .base import BaseCommand, BaseSetCommand, EnumAdapter, clone_state_with_key, recalculate_synthetic_tally, AutoMask


class SuperSourceProperties(BaseCommand):
    name = b'SSrc'
    format = Struct(
        'fill_source' / EnumAdapter(VideoSource)(Int16ub),
        'key_source' / EnumAdapter(VideoSource)(Int16ub),
        'foreground' / Flag,
        'pre_multiplied' / Flag,
        'clip' / Int16ub,
        'gain' / Int16ub,
        'invert_key' / Flag,
        'border_enabled' / Flag,
        'border_bevel' / EnumAdapter(BevelType)(Int8ub),
        Padding(1),
        'border_outer_width' / Int16ub,
        'border_inner_width' / Int16ub,
        'border_outer_softness' / Int8ub,
        'border_inner_softness' / Int8ub,
        'border_bevel_softness' / Int8ub,
        'border_bevel_position' / Int8ub,
        'border_hue' / Int16ub,
        'border_saturation' / Int16ub,
        'border_luma' / Int16ub,
        'light_source_direction' / Int16ub,
        'light_source_altitude' / Int8ub,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state, ssrc = clone_state_with_key(state, 'super_source')
        my_ssrc = ssrc.setdefault(0, {})

        my_ssrc['fill_source'] = self.fill_source
        my_ssrc['key_source'] = self.key_source
        my_ssrc['foreground'] = self.foreground
        my_ssrc['pre_multiplied'] = self.pre_multiplied
        my_ssrc['clip'] = self.clip
        my_ssrc['gain'] = self.gain
        my_ssrc['invert_key'] = self.invert_key

        my_ssrc['border'] = {
            'enabled': self.border_enabled,
            'outer_width': self.border_outer_width,
            'inner_width': self.border_inner_width,
            'inner_softness': self.border_inner_softness,
            'hue': self.border_hue,
            'saturation': self.border_saturation,
            'luma': self.border_luma,
            'bevel': {
                'type': self.border_bevel,
                'softness': self.border_bevel_softness,
                'position': self.border_bevel_position,
                'light_source': {
                    'direction': self.light_source_direction,
                    'altitude': self.light_source_altitude
                }
            }
        }

        return recalculate_synthetic_tally(new_state)


class SetSuperSourceProperties(BaseSetCommand):

    class Mask(AutoMask):
        format = BitStruct(
            Padding(12),
            'light_source_altitude' / Flag,
            'light_source_direction' / Flag,
            'border_luma' / Flag,
            'border_saturation' / Flag,
            'border_hue' / Flag,
            'bevel_position' / Flag,
            'bevel_softness' / Flag,
            'inner_softness' / Flag,
            'outer_softness' / Flag,
            'inner_width' / Flag,
            'outer_width' / Flag,
            'bevel' / Flag,
            'border_enabled' / Flag,
            'invert_key' / Flag,
            'gain' / Flag,
            'clip' / Flag,
            'pre_multiplied' / Flag,
            'foreground' / Flag,
            'key_source' / Flag,
            'fill_source' / Flag,
        )

    name = b'CSSc'
    format = Struct(
        'mask' / Rebuild(Mask.format, Mask.calculate),
        'fill_source' / EnumAdapter(VideoSource)(Default(Int16ub, 0)),
        'key_source' / EnumAdapter(VideoSource)(Default(Int16ub, 0)),
        'foreground' / Default(Flag, False),
        'pre_multiplied' / Default(Flag, False),
        'clip' / Default(Int16ub, 0),
        'gain' / Default(Int16ub, 0),
        'invert_key' / Default(Flag, False),
        'border_enabled' / Default(Flag, False),
        'bevel' / Default(Int8ub, 0),
        Padding(1),
        'outer_width' / Default(Int16ub, 0),
        'inner_width' / Default(Int16ub, 0),
        'outer_softness' / Default(Int8ub, 0),
        'inner_softness' / Default(Int8ub, 0),
        'bevel_softness' / Default(Int8ub, 0),
        'bevel_position' / Default(Int8ub, 0),
        'border_hue' / Default(Int16ub, 0),
        'border_saturation' / Default(Int16ub, 0),
        'border_luma' / Default(Int16ub, 0),
        'light_source_direction' / Default(Int16ub, 0),
        'light_source_altitude' / Default(Int8ub, 0),
        Padding(1)
    )
    maximum_version = 2.27


class SuperSourceV8Properties(BaseCommand):
    name = b'SSrc'
    minimum_version = 2.28
    format = Struct(
        'id' / Int8ub,
        Padding(1),
        'fill_source' / EnumAdapter(VideoSource)(Int16ub),
        'key_source' / EnumAdapter(VideoSource)(Int16ub),
        'foreground' / Flag,
        'pre_multiplied' / Flag,
        'clip' / Int16ub,
        'gain' / Int16ub,
        'invert_key' / Flag,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state, ssrc = clone_state_with_key(state, 'super_source')

        my_ssrc = ssrc.setdefault(self.id, {})

        my_ssrc['fill_source'] = self.fill_source
        my_ssrc['key_source'] = self.key_source
        my_ssrc['foreground'] = self.foreground
        my_ssrc['pre_multiplied'] = self.pre_multiplied
        my_ssrc['clip'] = self.clip
        my_ssrc['gain'] = self.gain
        my_ssrc['invert_key'] = self.invert_key

        return recalculate_synthetic_tally(new_state)


class SetSuperSourceV8Properties(BaseSetCommand):
    class Mask(AutoMask):
        format = BitStruct(
            Padding(2),
            'invert_key' / Flag,
            'gain' / Flag,
            'clip' / Flag,
            'pre_multiplied' / Flag,
            'foreground' / Flag,
            'key_source' / Flag,
            'fill_source' / Flag
        )
    name = b'CSSc'
    minimum_version = 2.28
    format = Struct(
        'mask' / Rebuild(Mask.format, Mask.calculate),
        'id' / Int8ub,
        'fill_source' / EnumAdapter(VideoSource)(Default(Int16ub, 0)),
        'key_source' / EnumAdapter(VideoSource)(Default(Int16ub, 0)),
        'foreground' / Default(Flag, False),
        'pre_multiplied' / Default(Flag, False),
        'clip' / Default(Int16ub, 0),
        'gain' / Default(Int16ub, 0),
        'invert_key' / Default(Flag, False),
        Padding(3)
    )


class SuperSourceV8BorderProperties(BaseCommand):
    name = b'SSBd'
    minimum_version = 2.28
    format = Struct(
        'id' / Int8ub,
        'enabled' / Flag,
        'bevel' / EnumAdapter(BevelType)(Int8ub),
        Padding(1),
        'outer_width' / Int16ub,
        'inner_width' / Int16ub,
        'outer_softness' / Int8ub,
        'inner_softness' / Int8ub,
        'bevel_softness' / Int8ub,
        'bevel_position' / Int8ub,
        'hue' / Int16ub,
        'saturation' / Int16ub,
        'luma' / Int16ub,
        'light_source_direction' / Int16ub,
        'light_source_altitude' / Int8ub,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state, ssrc = clone_state_with_key(state, 'super_source')

        my_ssrc = ssrc.setdefault(self.id, {})

        my_ssrc['border'] = {
            'enabled': self.enabled,
            'outer_width': self.outer_width,
            'inner_width': self.inner_width,
            'inner_softness': self.inner_softness,
            'hue': self.hue,
            'saturation': self.saturation,
            'luma': self.luma,
            'bevel': {
                'type': self.bevel,
                'softness': self.bevel_softness,
                'position': self.bevel_position,
                'light_source': {
                    'direction': self.light_source_direction,
                    'altitude': self.light_source_altitude
                }
            }
        }

        return new_state


class SetSuperSourceV8BorderProperties(BaseSetCommand):
    class Mask(AutoMask):
        format = BitStruct(
            'light_source_altitude' / Flag,
            'light_source_direction' / Flag,
            'luma' / Flag,
            'saturation' / Flag,
            'hue' / Flag,
            'bevel_position' / Flag,
            'bevel_softness' / Flag,
            'inner_softness' / Flag,
            'outer_softness' / Flag,
            'inner_width' / Flag,
            'outer_width' / Flag,
            'bevel' / Flag,
            'enabled' / Flag
        )
    name = b'CSBd'
    minimum_version = 2.28
    format = Struct(
        'mask' / Rebuild(Mask.format, Mask.calculate),
        Padding(1),
        'id' / Int8ub,
        'enabled' / Default(Flag, False),
        'bevel' / EnumAdapter(BevelType)(Default(Int8ub, 0)),
        'outer_width' / Default(Int16ub, 0),
        'inner_width' / Default(Int16ub, 0),
        'outer_softness' / Default(Int8ub, 0),
        'inner_softness' / Default(Int8ub, 0),
        'bevel_softness' / Default(Int8ub, 0),
        'bevel_position' / Default(Int8ub, 0),
        'hue' / Default(Int16ub, 0),
        'saturation' / Default(Int16ub, 0),
        'luma' / Default(Int16ub, 0),
        'light_source_direction' / Default(Int16ub, 0),
        'light_source-altitude' / Default(Int8ub, 0),
        Padding(3)
    )


class SuperSourceBoxProperties(BaseCommand):
    name = b'SSBP'
    format = Struct(
        'index' / Int8ub,
        'enabled' / Flag,
        'source' / EnumAdapter(VideoSource)(Int16ub),
        'position_x' / Int16sb,
        'position_y' / Int16sb,
        'size' / Int16ub,
        'crop' / Flag,
        Padding(1),
        'crop_top' / Int16ub,
        'crop_bottom' / Int16ub,
        'crop_left' / Int16ub,
        'crop_right' / Int16ub
    )

    def apply_to_state(self, state):
        new_state, ssrc = clone_state_with_key(state, 'super_source')
        boxes = ssrc.setdefault(0, {}).setdefault('boxes', {})

        boxes[self.index] = {
            'enabled': self.enabled,
            'source': self.source,
            'position': {
                'x': self.position_x,
                'y': self.position_y
            },
            'size': self.size,
            'crop': {
                'enabled': self.crop,
                'top': self.crop_top,
                'bottom': self.crop_bottom,
                'left': self.crop_left,
                'right': self.crop_right
            }
        }

        return recalculate_synthetic_tally(new_state)


class SuperSourceBoxV8Properties(BaseCommand):
    name = b'SSBP'
    minimum_version = 2.28
    format = Struct(
        'ssrc_id' / Int8ub,
        'index' / Int8ub,
        'enabled' / Flag,
        Padding(1),
        'source' / EnumAdapter(VideoSource)(Int16ub),
        'position_x' / Int16sb,
        'position_y' / Int16sb,
        'size' / Int16ub,
        'crop' / Flag,
        Padding(1),
        'crop_top' / Int16ub,
        'crop_bottom' / Int16ub,
        'crop_left' / Int16ub,
        'crop_right' / Int16ub,
        Padding(2)
    )

    def apply_to_state(self, state):
        new_state, ssrc = clone_state_with_key(state, 'super_source')
        boxes = ssrc.setdefault(self.ssrc_id, {}).setdefault('boxes', {})

        boxes[self.index] = {
            'enabled': self.enabled,
            'source': self.source,
            'position': {
                'x': self.position_x,
                'y': self.position_y
            },
            'size': self.size,
            'crop': {
                'enabled': self.crop,
                'top': self.crop_top,
                'bottom': self.crop_bottom,
                'left': self.crop_left,
                'right': self.crop_right
            }
        }

        return recalculate_synthetic_tally(new_state)
