from avista.devices.blackmagic.atem.commands.mix_effects import SetKeyerType
from avista.devices.blackmagic.atem.constants import KeyType


def test_set_keyer_type():
    cmd = SetKeyerType(index=0, key_index=1, type=KeyType.PATTERN)
    b = cmd.to_bytes()

    assert b[0:4] == b'CKTp'
    assert b[4] == 0x80  # = binary 10000000
