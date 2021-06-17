from avista.devices.blackmagic.atem.commands.tally import TallyByIndex


def test_tally_by_index():
    raw = b'TlIn\x00\x14\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    tlin = TallyByIndex.parse(raw)

    assert len(tlin.sources) == 20

    print(tlin.sources[2])
    assert tlin.sources[2].preview is True
