from avista.devices.blackmagic.atem.commands.audio import ResetInputAudioMeterPeaks, ResetMasterAudioMeterPeaks
from avista.devices.blackmagic.atem.constants import AudioSource


def test_reset_master_audio_meter_peaks():
    cmd = ResetMasterAudioMeterPeaks()
    b = cmd.to_bytes()

    assert b[0:4] == b'RAMP'
    assert b[4] == 4  # Master == 4
    assert b[6] == 0  # Source byte 1
    assert b[7] == 0  # Source byte 2
    assert b[8] == 1  # 1 = master


def test_reset_input_audio_meter_peaks():
    cmd = ResetInputAudioMeterPeaks(source=AudioSource.INPUT_18)
    b = cmd.to_bytes()

    assert b[0:4] == b'RAMP'
    assert b[4] == 2  # Input == 2
    assert b[6] == 0  # Source byte 1
    assert b[7] == 18  # Source byte 2
    assert b[8] == 0  # 1 = master
