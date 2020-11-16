from avista.devices.blackmagic.atem.constants import MediaPoolFileType
from construct import Struct, Bytes, Const, Flag, Int8ub, Int16ub, CString, Padding, GreedyBytes
from .base import BaseCommand, EnumAdapter


class MediaPoolFrameDescription(BaseCommand):
    name = b'MPfe'
    format = Struct(
        'file_type' / EnumAdapter(MediaPoolFileType)(Int8ub),
        'index' / Int16ub,
        'used' / Flag,
        'hash' / Bytes(16),
        'filename' / CString('utf-8')
    )


class MediaPoolClipDescription(BaseCommand):
    name = b'MPCS'
    format = Struct(
        'index' / Int8ub,
        'used' / Flag,
        'name' / CString('utf-8'),
        'frame_count' / Int16ub
    )


class MediaPoolUnknownFM(BaseCommand):
    name = b'MPfM'
    format = Struct(
        'data' / GreedyBytes
    )
