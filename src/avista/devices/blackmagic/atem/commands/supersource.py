from avista.devices.blackmagic.atem.constants import BevelType, VideoSource
from construct import BitStruct, Struct, Int8ub, Int16ub, Int16sb, Padding, Flag

from .base import BaseCommand, EnumAdapter, clone_state_with_key, recalculate_synthetic_tally


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


class SuperSourceV8BorderProperties(BaseCommand):
    name = b'SSBd'
    format = Struct(
        'ssrc_id' / Int8ub,
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
        new_state, ssrc = clone_state_with_key('super_source')
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
        new_state, ssrc = clone_state_with_key('super_source')
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
