from avista.devices.blackmagic.atem.constants import MediaPoolFileType
from construct import Struct, Bytes, Const, Flag, Int8ub, Int16ub, CString, Padding, GreedyBytes
from .base import BaseCommand, EnumAdapter, PaddedCStringAdapter, clone_state_with_key


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


class MediaPoolLockState(BaseCommand):
    name = b'LKST'
    format = Struct(
        'index' / Int16ub,
        'lock' / Int16ub
    )

    def apply_to_state(self, state):
        new_state, media = clone_state_with_key(state, 'media_pool')
        locks = media.setdefault('locks', {})

        locks[self.index] = self.lock

        return new_state


class MediaPlayerSplit(BaseCommand):
    name = b'MPSp'
    format = Struct(
        'clip_1' / Int16ub,
        'clip_2' / Int16ub
    )

    def apply_to_state(self, state):
        new_state, media = clone_state_with_key(state, 'media_player')
        storage = media.setdefault('storage', {})

        storage['clip_1'] = self.clip_1
        storage['clip_2'] = self.clip_2

        return new_state


class MediaPlayerSource(BaseCommand):
    name = b'MPCE'
    format = Struct(
        'index' / Int8ub,
        'type' / Int8ub,
        'still_index' / Int8ub,
        'clip_index' / Int8ub
    )

    def apply_to_state(self, state):
        new_state, media = clone_state_with_key(state, 'media_player')
        source = media.setdefault('source', {})

        source[self.index] = {
            'type': self.type,
            'still_index': self.still_index,
            'clip_index': self.clip_index
        }

        return new_state


class MediaPlayerAudioSource(BaseCommand):
    name = b'MPAS'
    format = Struct(
        'index' / Int8ub,
        'used' / Flag,
        Padding(16),
        'name' / PaddedCStringAdapter(Bytes(16)),
        Padding(50)
    )

    def apply_to_state(self, state):
        new_state, media = clone_state_with_key(state, 'media_player')
        audio = media.setdefault('audio', {})

        audio[self.index] = {
            'used': self.used,
            'name': self.name
        }

        return new_state
