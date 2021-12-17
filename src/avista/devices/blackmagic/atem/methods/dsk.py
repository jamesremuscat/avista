from avista.core import expose

from avista.devices.blackmagic.atem.commands.dsk import \
    DownstreamKeyerPerformAuto, SetDownstreamKeyerOnAir, SetDownstreamKeyerTie


class DSK(object):
    @expose
    def set_dsk_on_air(self, index, on_air):
        self.get_protocol().send_command(
            SetDownstreamKeyerOnAir(
                index=index,
                on_air=on_air
            )
        )

    @expose
    def set_dsk_tie(self, index, tie):
        self.get_protocol().send_command(
            SetDownstreamKeyerTie(
                index=index,
                tie=tie
            )
        )

    @expose
    def dsk_perform_auto(self, index):
        self.get_protocol().send_command(
            DownstreamKeyerPerformAuto(
                index=index
            )
        )
