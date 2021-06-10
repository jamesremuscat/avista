from avista.core import expose

from avista.devices.blackmagic.atem.commands.mix_effects import \
    SetProgramInput, SetPreviewInput, PerformAuto, \
    PerformCut, TransitionSelectionField, SetTransitionProperties

from avista.devices.blackmagic.atem.constants import VideoSource, TransitionStyle


class MixEffects(object):
    @expose
    def set_preview_input(self, input, me=0):
        cmd = SetPreviewInput(source=VideoSource(input), index=me)
        self.get_protocol().send_command(cmd)

    @expose
    def set_program_input(self, input, me=0):
        cmd = SetProgramInput(source=VideoSource(input), index=me)
        self.get_protocol().send_command(cmd)

    @expose
    def perform_cut(self, me=0):
        cmd = PerformCut(index=me)
        self.get_protocol().send_command(cmd)

    @expose
    def perform_auto(self, me=0):
        cmd = PerformAuto(index=me)
        self.get_protocol().send_command(cmd)

    @expose
    def set_transition_properties(self, style=None, background=None, key_1=None, key_2=None, key_3=None, key_4=None, me=0):
        tie = TransitionSelectionField.parse(
            TransitionSelectionField.build(
                dict(
                    background=background,
                    key_1=key_1,
                    key_2=key_2,
                    key_3=key_3,
                    key_4=key_4
                )
            )
        )

        self.get_protocol().send_command(
            SetTransitionProperties(
                style=TransitionStyle(style),
                next=tie,
                index=me
            )
        )
