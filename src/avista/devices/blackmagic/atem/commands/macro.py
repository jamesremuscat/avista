from construct import Struct, Flag, Int16ub, PaddedString, this
from .base import BaseCommand, clone_state_with_key

import copy


class MacroProperties(BaseCommand):
    name = b'MPrp'
    format = Struct(
        'id' / Int16ub,
        'used' / Flag,
        'has_unsupported_ops' / Flag,
        'name_length' / Int16ub,
        'description_length' / Int16ub,
        'name' / PaddedString(this.name_length, 'utf-8'),
        'description' / PaddedString(this.description_length, 'utf-8'),
    )

    def apply_to_state(self, state):
        new_state, macros = clone_state_with_key(state, 'macros')

        macro = macros.setdefault(self.id, {})
        macro['used'] = self.used
        macro['name'] = self.name
        macro['description'] = self.description

        return new_state
