from avista.core import expose
from avista.devices.blackmagic.atem.constants import MacroActionType
from avista.devices.blackmagic.atem.commands.macro import MacroAction


class Macro(object):
    @expose
    def trigger_macro(self, macro_index):
        self.get_protocol().send_command(
            MacroAction(
                index=macro_index,
                action=MacroActionType.RUN_MACRO
            )
        )
