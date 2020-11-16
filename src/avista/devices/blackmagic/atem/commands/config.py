from construct import Struct, Const, Flag, Int8ub, Int16ub, PaddedString, Padding
from recordclass import recordclass
from .base import BaseCommand


class Version(BaseCommand):
    format = Struct(
        '_name' / Const(b'_ver'),
        'major' / Int16ub,
        'minor' / Int16ub
    )


class ProductName(BaseCommand):
    format = Struct(
        '_name' / Const(b'_pin'),
        'name' / PaddedString(44, 'utf8')
    )


class TopologyV7(BaseCommand):
    format = Struct(
        '_name' / Const(b'_top'),
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


class TopologyV8(BaseCommand):
    format = Struct(
        '_name' / Const(b'_top'),
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


class TopologyV811(BaseCommand):
    format = Struct(
        '_name' / Const(b'_top'),
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
