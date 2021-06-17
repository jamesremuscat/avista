from avista.devices.blackmagic.atem.commands.supersource import SetSuperSourceProperties


def test_set_supersource_properties_mask():
    cmd = SetSuperSourceProperties(bevel_softness=3)
    obj = cmd.to_object()
    assert obj.mask.bevel_softness is True

    true_values = [v for v in obj.mask.values() if v is True]

    assert len(true_values) == 1

    cmd2 = SetSuperSourceProperties(clip=123, gain=456, border_hue=789)
    obj2 = cmd2.to_object()
    assert obj2.mask.clip is True
    assert obj2.mask.gain is True
    assert obj2.mask.border_hue is True
