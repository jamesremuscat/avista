from avista.devices.blackmagic.atem.constants import SDI3GOutputLevel, VideoMode
from construct import Bytes, BitStruct, Struct, Const, Flag, Int8ub, Int16ub, Int32ub, Padding
from .base import BaseCommand, EnumAdapter, EnumFlagAdapter, clone_state_with_key, PaddedCStringAdapter

import copy


class Version(BaseCommand):
    name = b'_ver'
    format = Struct(
        'major' / Int16ub,
        'minor' / Int16ub
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        config['version'] = {
            'major': self.major,
            'minor': self.minor
        }
        return new_state


class ProductName(BaseCommand):
    name = b'_pin'
    format = Struct(
        'name' / PaddedCStringAdapter(Bytes(44))
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        config['name'] = self.name.strip()
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
        new_state, mes = clone_state_with_key(state, 'mes')
        me = mes.setdefault(self.id, {})
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
        new_state, config = clone_state_with_key(state, 'config')
        mpl = config.setdefault('media_pool', {})
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

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        mvc = config.setdefault('multiviewer', {})
        mvc['count'] = self.count
        mvc['window_count'] = self.window_count
        mvc['can_route_inputs'] = self.can_route_inputs
        mvc['can_swap_program_preview'] = self.can_swap_program_preview
        mvc['can_toggle_safe_area'] = self.can_toggle_safe_area
        return new_state


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

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        mvc = config.setdefault('multiviewer', {})
        mvc['count'] = self.count
        mvc['window_count'] = self.window_count
        mvc['can_route_inputs'] = self.can_route_inputs
        mvc['supports_vu_meters'] = self.supports_vu_meters
        mvc['can_swap_program_preview'] = self.can_swap_program_preview
        mvc['can_toggle_safe_area'] = self.can_toggle_safe_area
        mvc['supports_quadrants'] = self.supports_quadrants
        return new_state


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

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        mvc = config.setdefault('multiviewer', {})
        mvc['window_count'] = self.window_count
        mvc['can_change_layout'] = self.can_change_layout
        mvc['can_route_inputs'] = self.can_route_inputs
        mvc['supports_vu_meters'] = self.supports_vu_meters
        mvc['can_swap_program_preview'] = self.can_swap_program_preview
        mvc['can_toggle_safe_area'] = self.can_toggle_safe_area
        mvc['supports_quadrants'] = self.supports_quadrants
        return new_state


class AudioMixerConfig(BaseCommand):
    name = b'_AMC'
    format = Struct(
        'inputs' / Int8ub,
        'monitors' / Int8ub,
        'headphones' / Int8ub
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        audio = config.setdefault('audio', {})
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
        new_state, stateObj = clone_state_with_key(state, 'state')
        stateObj['video_mode'] = self.mode
        return new_state


class DownConvertVideoMode(BaseCommand):
    name = b'DHVm'
    format = Struct(
        'core_mode' / EnumAdapter(VideoMode)(Int8ub),
        'down_converted_mode' / EnumAdapter(VideoMode)(Int8ub),
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        dc = config.setdefault('downconverter', {})
        dc[self.core_mode] = self.down_converted_mode
        return new_state


class VideoMixerConfig(BaseCommand):
    name = b'_VMC'
    format = Struct(
        'available_modes' / EnumFlagAdapter(VideoMode)(Int32ub)
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
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
        new_state, stateObj = clone_state_with_key(state, 'state')
        stateObj['power'] = {
            'main': self.power.main,
            'backup': self.power.backup
        }
        return new_state


class SDI3GOutputLevel(BaseCommand):
    name = b'V3sl'
    format = Struct(
        'level' / EnumAdapter(SDI3GOutputLevel)(Int8ub)
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        config['sdi_3g_output_level'] = self.level
        return new_state


class MacroPoolConfig(BaseCommand):
    name = b'_MAC'
    format = Struct(
        'count' / Int8ub,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        config['macro_pool_size'] = self.count
        return new_state


class TallyChannelConfig(BaseCommand):
    name = b'_TlC'
    format = Struct(
        Padding(4),
        'count' / Int8ub,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        config['tally_channels'] = self.count
        return new_state


class TimecodeLock(BaseCommand):
    name = b'TcLk'
    format = Struct(
        'locked' / Flag,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state, stateObj = clone_state_with_key(state, 'state')
        stateObj['timecode_locked'] = self.locked
        return new_state


class InitComplete(BaseCommand):
    name = b'InCm'
    format = Struct(
        'complete' / Flag,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state, stateObj = clone_state_with_key(state, 'state')
        stateObj['initialized'] = self.complete
        return new_state


class SuperSourceBoxCount(BaseCommand):
    name = b'_SSC'
    format = Struct(
        'count' / Int8ub,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state, ssrc = clone_state_with_key(state, 'super_source')
        for ss in ssrc.values():
            boxes = ss.setdefault('boxes', {})
            for i in range(self.count):
                boxes[i] = {"enabled": False}

        return new_state
