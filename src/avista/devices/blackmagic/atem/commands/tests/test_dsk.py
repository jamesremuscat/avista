from avista.devices.blackmagic.atem.commands.dsk import SetDownstreamKeyerOnAir


def test_set_dsk_on_air():
    cmd = SetDownstreamKeyerOnAir(index=0, on_air=True)
    b = cmd.to_bytes()

    assert b[0:4] == b'CDsL'
    assert b[4] == 0  # Index
    assert b[5] == 0x1  # On air
