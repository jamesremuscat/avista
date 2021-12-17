from avista.core import expose

from avista.devices.blackmagic.atem.commands.dsk import \
    SetDownstreamKeyerOnAir

from avista.devices.blackmagic.atem.constants import VideoSource


class DSK(object):
    @expose
    def set_dsk_on_air(self, index, on_air):
        self.get_protocol().send_command(
            SetDownstreamKeyerOnAir(
                index=index,
                on_air=on_air
            )
        )
