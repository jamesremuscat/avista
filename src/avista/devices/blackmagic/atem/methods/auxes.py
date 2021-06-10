from avista.core import expose

from avista.devices.blackmagic.atem.commands.auxes import \
    SetAuxSource

from avista.devices.blackmagic.atem.constants import VideoSource


class Auxes(object):
    @expose
    def set_aux_source(self, aux, source):
        self.get_protocol().send_command(
            SetAuxSource(
                index=aux,
                source=VideoSource(source)
            )
        )
