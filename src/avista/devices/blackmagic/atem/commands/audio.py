from construct import Struct, Flag, Int8ub, Int16ub, Int16sb, Padding, Rebuild, len_, this

from avista.devices.blackmagic.atem.constants import AudioSource, AudioSourceType, AudioSourcePlugType, AudioMixOption
from .base import BaseCommand, EnumAdapter

import copy


class AudioMixerInput(BaseCommand):
    name = b'AMIP'
    format = Struct(
        'source' / EnumAdapter(AudioSource)(Int16ub),
        'type' / EnumAdapter(AudioSourceType)(Int8ub),
        Padding(3),
        'from_media_player' / Flag,
        'plug_type' / EnumAdapter(AudioSourcePlugType)(Int8ub),
        'mix_option' / EnumAdapter(AudioMixOption)(Int8ub),
        Padding(1),
        'volume' / Int16ub,
        'balance' / Int16sb,
        Padding(1)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        input = new_state.setdefault('audio_sources', {}).setdefault(self.source, {})

        input['type'] = self.type
        input['from_media_player'] = self.from_media_player
        input['plug_type'] = self.plug_type
        input['mix_option'] = self.mix_option
        input['volume'] = self.volume
        input['balance'] = self.balance

        return new_state


class AudioMixerMaster(BaseCommand):
    name = b'AMMO'
    format = Struct(
        'volume' / Int16ub,
        Padding(6)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        new_state['audio'] = copy.copy(state.get('audio', {}))

        master = {
            'volume': self.volume
        }

        new_state['audio']['master'] = master
        return new_state


class AudioMixerMonitor(BaseCommand):
    name = b'AMmO'
    format = Struct(
        'enabled' / Flag,
        Padding(1),
        'volume' / Int16ub,
        'mute' / Flag,
        'solo' / Flag,
        'solo_input' / EnumAdapter(AudioSource)(Int16ub),
        'dim' / Flag,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        new_state['audio'] = copy.copy(state.get('audio', {}))

        monitor = {
            'enabled': self.enabled,
            'volume': self.volume,
            'mute': self.mute,
            'solo': self.solo,
            'solo_input': self.solo_input,
            'dim': self.dim
        }

        new_state['audio']['monitor'] = monitor
        return new_state


class AudioMixerTally(BaseCommand):
    name = b'AMTl'
    format = Struct(
        'source_count' / Rebuild(Int16ub, len_(this.sources)),
        'sources' / Struct(
            'source' / EnumAdapter(AudioSource)(Int16ub),
            'is_mixed_in' / Flag
        )[this.source_count]
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        new_state['audio'] = copy.copy(state.get('audio', {}))

        tally = {}

        for source in self.sources:
            tally[source.source] = source.is_mixed_in

        new_state['audio']['tally'] = tally
        return new_state


class AudioFollowVideo(BaseCommand):
    name = b'AMPP'
    format = Struct(
        'enabled' / Flag,
        Padding(3)
    )

    def apply_to_state(self, state):
        new_state = copy.copy(state)
        new_state['audio'] = copy.copy(state.get('audio', {}))

        new_state['audio']['afv'] = self.enabled
        return new_state
