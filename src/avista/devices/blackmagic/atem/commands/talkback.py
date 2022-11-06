from avista.devices.blackmagic.atem.constants import VideoSource
from construct import Struct, Int8ub, Int16ub, Padding, Flag

from .base import BaseCommand, EnumAdapter, clone_state_with_key


class TalkbackMixerInputProperties(BaseCommand):
    name = b'TMIP'
    format = Struct(
        'channel' / Int8ub,
        Padding(1),
        'video_source' / EnumAdapter(VideoSource)(Int16ub),
        'can_mute_sdi' / Flag,
        'current_input_supports_mute_sdi' / Flag,
        'mute_sdi' / Flag,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state, talkback = clone_state_with_key(state, 'talkback')

        channel = talkback.setdefault(self.channel, {})

        channel[self.video_source] = {
            'can_mute_sdi': self.can_mute_sdi,
            'current_input_supports_mute_sdi': self.current_input_supports_mute_sdi,
            'mute_sdi': self.mute_sdi
        }

        return new_state
