from avista.devices.blackmagic.atem.constants import ExternalPortType, InternalPortType, MEAvailability, \
    MultiviewLayout, SourceAvailability, VideoSource, VideoMode
from construct import Adapter, Struct, Enum, Flag, FlagsEnum, Int8ub, Int16ub, PaddedString, Padding, this
from .base import BaseCommand, EnumAdapter, EnumFlagAdapter, PaddedCStringAdapter


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


class MultiviewVideoMode(BaseCommand):
    name = b'MvVM'
    format = Struct(
        'core_video_mode' / VideoModeAdapter(Int8ub),
        'multiview_video_mode' / VideoModeAdapter(Int8ub),
    )


class MultiviewLayout(BaseCommand):
    name = b'MvPr'
    format = Struct(
        'index' / Int8ub,
        'layout' / EnumAdapter(MultiviewLayout)(Int8ub)
    )


class MultiviewWindowVUMeter(BaseCommand):
    name = b'VuMC'
    format = Struct(
        'index' / Int8ub,
        'window_index' / Int8ub,
        'enabled' / Flag
    )


class MultiviewWindowSafeArea(BaseCommand):
    name = b'SaMw'
    format = Struct(
        'index' / Int8ub,
        'window_index' / Int8ub,
        'enabled' / Flag
    )


class MultiviewInput(BaseCommand):
    name = b'MvIn'
    format = Struct(
        'index' / Int8ub,
        'window_index' / Int8ub,
        'source' / EnumAdapter(VideoSource)(Int16ub)
    )
