from avista.core import expose


from avista.devices.blackmagic.atem.commands.audio import ResetMasterAudioMeterPeaks


class Audio(object):
    @expose
    def reset_master_audio_meter_peaks(self):
        self.get_protocol().send_command(
            ResetMasterAudioMeterPeaks()
        )

    @expose
    def reset_input_audio_meter_peaks(self, source):
        self.get_protocol().send_command(
            ResetMasterAudioMeterPeaks(source=source)
        )
