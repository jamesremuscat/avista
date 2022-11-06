from avista.devices.blackmagic.atem.commands.settings import MultiviewOpacity


def test_multiview_opacity():
    raw = b'VuMo\x01dPr'

    vumo = MultiviewOpacity.parse(raw)

    state = vumo.apply_to_state({})

    assert state == {
        'config': {
            'multiviewers': {
                1: {
                    'opacity': 100
                }
            }
        }
    }
