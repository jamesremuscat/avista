from avista.devices.blackmagic.atem.constants import VideoMode
from construct import BitStruct, Struct, Const, Flag, Int8ub, Int16ub, Int32ub, PaddedString, Padding
from .base import BaseCommand, EnumAdapter, EnumFlagAdapter

import copy


class Version(BaseCommand):
    name = b'_ver'
    format = Struct(
        'major' / Int16ub,
        'minor' / Int16ub
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        new_state.setdefault('config', {})['version'] = {
            'major': self.major,
            'minor': self.minor
        }
        return new_state


class ProductName(BaseCommand):
    name = b'_pin'
    format = Struct(
        'name' / PaddedString(44, 'utf8')
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        new_state.setdefault('config', {})['name'] = self.name
        return new_state


class TopologyBase(BaseCommand):
    name = b'_top'
    minimum_version = 99999

    def apply_to_state(self, state):

        new_state = copy.copy(state)

        new_state['mes'] = {idx: {} for idx in range(self.mes)}
        new_state['dsks'] = {idx: {} for idx in range(self.dsks)}
        new_state['auxes'] = {idx: {} for idx in range(self.auxes)}
        new_state['super_sources'] = {idx: {} for idx in range(self.super_sources)}

        return new_state


class TopologyV7(TopologyBase):
    minimum_version = 2.00
    format = Struct(
        'mes' / Int8ub,
        'sources' / Int8ub,
        'dsks' / Int8ub,
        'auxes' / Int8ub,
        'mix_minus_outputs' / Int8ub,
        'media_players' / Int8ub,
        'serial_ports' / Int8ub,
        'hyperdecks' / Int8ub,
        'dves' / Int8ub,
        'stingers' / Int8ub,
        'super_sources' / Int8ub,
    )


class TopologyV8(TopologyBase):
    name = b'_top'
    minimum_version = 2.28
    format = Struct(
        'mes' / Int8ub,
        'sources' / Int8ub,
        'dsks' / Int8ub,
        'auxes' / Int8ub,
        'mix_minus_outputs' / Int8ub,
        'media_players' / Int8ub,
        'serial_ports' / Int8ub,
        'hyperdecks' / Int8ub,
        'dves' / Int8ub,
        'stingers' / Int8ub,
        'super_sources' / Int8ub,
        Padding(1),
        'talkback_channels' / Int8ub,
        Padding(4),
        'camera_control' / Flag,
        Padding(3),
        'advanced_chroma_keyers' / Flag,
        'only_configurable_outputs' / Flag
    )


class TopologyV811(TopologyBase):
    name = b'_top'
    minimum_version = 2.30
    format = Struct(
        'mes' / Int8ub,
        'sources' / Int8ub,
        'dsks' / Int8ub,
        'auxes' / Int8ub,
        'mix_minus_outputs' / Int8ub,
        'media_players' / Int8ub,
        'multiviewers' / Int8ub,
        'serial_ports' / Int8ub,
        'hyperdecks' / Int8ub,
        'dves' / Int8ub,
        'stingers' / Int8ub,
        'super_sources' / Int8ub,
        Padding(1),
        'talkback_channels' / Int8ub,
        Padding(4),
        'camera_control' / Flag,
        Padding(3),
        'advanced_chroma_keyers' / Flag,
        'only_configurable_outputs' / Flag
    )


class MixEffectBusConfig(BaseCommand):
    name = b'_MeC'
    format = Struct(
        'id' / Int8ub,
        'keyers' / Int8ub
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        me = new_state.setdefault('mes', {}).setdefault(self.id, {})
        me['keyers'] = {
            idx: {} for idx in range(self.keyers)
        }
        return new_state


class MediaPoolConfig(BaseCommand):
    name = b'_mpl'
    format = Struct(
        'stills' / Int8ub,
        'clips' / Int8ub
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        mpl = new_state.setdefault('config', {}).setdefault('media_pool', {})
        mpl['stills'] = self.stills
        mpl['clips'] = self.clips
        return new_state


class MultiviewerConfigV7(BaseCommand):
    name = b'_MvC'
    format = Struct(
        'count' / Int8ub,
        'window_count' / Int8ub,
        Padding(1),
        'can_route_inputs' / Flag,
        Padding(1),
        'can_swap_program_preview' / Flag,
        Padding(1),
        'can_toggle_safe_area' / Flag
    )


class MultiviewerConfigV8(BaseCommand):
    name = b'_MvC'
    minimum_version = 2.28
    format = Struct(
        'count' / Int8ub,
        'window_count' / Int8ub,
        Padding(1),
        'can_route_inputs' / Flag,
        Padding(2),
        'supports_vu_meters' / Flag,
        'can_toggle_safe_area' / Flag,
        'can_swap_program_preview' / Flag,
        'supports_quadrants' / Flag
    )


class MultiviewerConfigV811(BaseCommand):
    name = b'_MvC'
    minimum_version = 2.30
    format = Struct(
        'window_count' / Int8ub,
        'can_change_layout' / Flag,
        'can_route_inputs' / Flag,
        Padding(2),
        'supports_vu_meters' / Flag,
        'can_toggle_safe_area' / Flag,
        'can_swap_program_preview' / Flag,
        'supports_quadrants' / Flag
    )


class AudioMixerConfig(BaseCommand):
    name = b'_AMC'
    format = Struct(
        'inputs' / Int8ub,
        'monitors' / Int8ub,
        'headphones' / Int8ub
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        audio = new_state.setdefault('config', {}).setdefault('audio', {})
        audio['input_count'] = self.inputs
        audio['monitor_count'] = self.monitors
        audio['headphones_count'] = self.headphones
        return new_state


class VideoModeConfig(BaseCommand):
    name = b'VidM'
    format = Struct(
        'mode' / EnumAdapter(VideoMode)(Int8ub)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        new_state.setdefault('state', {})['video_mode'] = self.mode
        return new_state


class DownConvertVideoMode(BaseCommand):
    name = b'DHVm'
    format = Struct(
        'core_mode' / EnumAdapter(VideoMode)(Int8ub),
        'down_converted_mode' / EnumAdapter(VideoMode)(Int8ub),
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        config = new_state.setdefault('config', {}).setdefault('downconverter', {})
        config[self.core_mode] = self.down_converted_mode
        return new_state


class VideoMixerConfig(BaseCommand):
    name = b'_VMC'
    format = Struct(
        'available_modes' / EnumFlagAdapter(VideoMode)(Int32ub)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        config = new_state.setdefault('config', {})
        config['available_video_modes'] = self.available_modes
        return new_state


class PowerState(BaseCommand):
    name = b'Powr'
    format = Struct(
        'power' / BitStruct(
            'main' / Flag,
            'backup' / Flag,
            Padding(6)
        ),
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        new_state.setdefault('state', {})['power'] = {
            'main': self.power.main,
            'backup': self.power.backup
        }
        return new_state
