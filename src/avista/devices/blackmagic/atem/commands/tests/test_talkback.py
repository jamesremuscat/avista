from avista.devices.blackmagic.atem.constants import VideoSource
from avista.devices.blackmagic.atem.commands.talkback import TalkbackMixerInputProperties


def test_talkback_mixer_input_properties():
    raw = b'TMIP\x00\x1c\x00\x0b\x00\x01\x00S'

    tmip = TalkbackMixerInputProperties.parse(raw)

    state = tmip.apply_to_state({})

    assert state['talkback'][0] == {
        VideoSource.INPUT_11: {
            'can_mute_sdi': False,
            'current_input_supports_mute_sdi': True,
            'mute_sdi': False
        }
    }
