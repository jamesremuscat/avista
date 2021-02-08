from avista.devices.blackmagic.atem.constants import ExternalPortType, InternalPortType, MEAvailability, \
    MultiviewLayout, SourceAvailability, VideoSource, VideoMode
from construct import Adapter, Struct, Enum, Flag, FlagsEnum, Int8ub, Int16ub, PaddedString, Padding, this
from .base import BaseCommand, EnumAdapter, EnumFlagAdapter, PaddedCStringAdapter, clone_state_with_key


ExternalPortTypeAdapter = EnumAdapter(ExternalPortType)
InternalPortTypeAdapter = EnumAdapter(InternalPortType)
VideoModeAdapter = EnumAdapter(VideoMode)


class InputProperties(BaseCommand):
    name = b'InPr'
    format = Struct(
        'id' / EnumAdapter(VideoSource)(Int16ub),
        'name' / PaddedCStringAdapter(PaddedString(20, 'utf-8')),
        'short_name' / PaddedCStringAdapter(PaddedString(4, 'utf-8')),
        'are_names_default' / Flag,
        Padding(1),
        'available_external_ports' / EnumFlagAdapter(ExternalPortType)(Int16ub),
        'external_port_type' / ExternalPortTypeAdapter(Int16ub),
        'internal_port_type' / InternalPortTypeAdapter(Int8ub),
        'source_availability' / EnumFlagAdapter(SourceAvailability)(Int8ub),
        'me_availability' / EnumFlagAdapter(MEAvailability)(Int8ub)
    )

    def apply_to_state(self, state):
        new_state, sources = clone_state_with_key(state, 'sources')

        source = sources.setdefault(self.id, {})
        source['id'] = self.id
        source['name'] = self.name
        source['short_name'] = self.short_name
        source['names_are_default'] = self.are_names_default
        # Spammy!
        # source['available_external_ports'] = self.available_external_ports
        # source['external_port_type'] = self.external_port_type
        source['internal_port_type'] = self.internal_port_type
        source['me_availability'] = self.me_availability

        return new_state


class MultiviewVideoMode(BaseCommand):
    name = b'MvVM'
    format = Struct(
        'core_video_mode' / VideoModeAdapter(Int8ub),
        'multiview_video_mode' / VideoModeAdapter(Int8ub),
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        mvw_config = config.setdefault('multiviewers', {}).setdefault('video_modes', {})

        mvw_config[self.core_video_mode] = self.multiview_video_mode
        return new_state


class MultiviewLayout(BaseCommand):
    name = b'MvPr'
    format = Struct(
        'index' / Int8ub,
        'layout' / EnumAdapter(MultiviewLayout)(Int8ub)
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        mvw_config = config.setdefault('multiviewers', {}).setdefault(self.index, {})
        mvw_config['layout'] = self.layout
        return new_state


class MultiviewWindowVUMeter(BaseCommand):
    name = b'VuMC'
    format = Struct(
        'index' / Int8ub,
        'window_index' / Int8ub,
        'enabled' / Flag
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        mvw_config = config.setdefault('multiviewers', {}).setdefault(self.index, {})
        window = mvw_config.setdefault('windows', {}).setdefault(self.window_index, {})
        window['vu_meter_enabled'] = self.enabled
        return new_state


class MultiviewWindowSafeArea(BaseCommand):
    name = b'SaMw'
    format = Struct(
        'index' / Int8ub,
        'window_index' / Int8ub,
        'enabled' / Flag
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        mvw_config = config.setdefault('multiviewers', {}).setdefault(self.index, {})
        window = mvw_config.setdefault('windows', {}).setdefault(self.window_index, {})
        window['safe_area_enabled'] = self.enabled
        return new_state


class MultiviewInput(BaseCommand):
    name = b'MvIn'
    format = Struct(
        'index' / Int8ub,
        'window_index' / Int8ub,
        'source' / EnumAdapter(VideoSource)(Int16ub)
    )

    def apply_to_state(self, state):
        new_state, config = clone_state_with_key(state, 'config')
        mvw_config = config.setdefault('multiviewers', {}).setdefault(self.index, {})
        window = mvw_config.setdefault('windows', {}).setdefault(self.window_index, {})
        window['source'] = self.source
        return new_state
