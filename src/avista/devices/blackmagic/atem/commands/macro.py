from construct import Struct, Flag, Int16ub, PaddedString, this
from .base import BaseCommand


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
