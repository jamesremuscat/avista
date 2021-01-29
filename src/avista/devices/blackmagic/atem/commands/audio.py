from construct import Struct, Flag, Int8ub, Int16ub, Int16sb, Padding, Rebuild, len_, this

from avista.devices.blackmagic.atem.constants import AudioSource, AudioSourceType, AudioSourcePlugType, AudioMixOption
from .base import BaseCommand, EnumAdapter


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


class AudioMixerMaster(BaseCommand):
    name = b'AMMO'
    format = Struct(
        'volume' / Int16ub,
        Padding(6)
    )


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


class AudioMixerTally(BaseCommand):
    name = b'AMTl'
    format = Struct(
        'source_count' / Rebuild(Int16ub, len_(this.sources)),
        'sources' / Struct(
            'source' / EnumAdapter(AudioSource)(Int16ub),
            'is_mixed_in' / Flag
        )[this.source_count]
    )
