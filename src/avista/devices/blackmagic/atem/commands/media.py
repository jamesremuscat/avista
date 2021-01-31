from avista.devices.blackmagic.atem.constants import MediaPoolFileType
from construct import Struct, Bytes, Const, Flag, Int8ub, Int16ub, CString, Padding, GreedyBytes
from .base import BaseCommand, EnumAdapter, clone_state_with_key

import copy


class MediaPoolFrameDescription(BaseCommand):
    name = b'MPfe'
    format = Struct(
        'file_type' / EnumAdapter(MediaPoolFileType)(Int8ub),
        'index' / Int16ub,
        'used' / Flag,
        'hash' / Bytes(16),
        'filename' / CString('utf-8')
    )

    def apply_to_state(self, state):
        new_state, media = clone_state_with_key(state, 'media_pool')
        frame_pool = media.setdefault('frames', {})

        frame_pool[self.index] = {
            'file_type': self.file_type,
            'used': self.used,
            'hash': self.hash,
            'filename': self.filename
        }

        return new_state


class MediaPoolClipDescription(BaseCommand):
    name = b'MPCS'
    format = Struct(
        'index' / Int8ub,
        'used' / Flag,
        'name' / CString('utf-8'),
        'frame_count' / Int16ub
    )

    def apply_to_state(self, state):
        new_state, media = clone_state_with_key(state, 'media_pool')
        clip_pool = media.setdefault('clip', {})

        clip_pool[self.index] = {
            'name': self.name,
            'used': self.used,
            'frame_count': self.frame_count
        }

        return new_state


class MediaPoolUnknownFM(BaseCommand):
    name = b'MPfM'
    format = Struct(
        'data' / GreedyBytes
    )

    def apply_to_state(self, state):
        return state
