from construct import Adapter, Const


def EnumAdapter(enum_class):
    class _EnumAdapter(Adapter):
        def _decode(self, obj, context, path):
            return enum_class(obj)

        def _encode(self, obj, context, path):
            return obj.value
    return _EnumAdapter


def EnumFlagAdapter(enum_class):
    class _EnumFlagAdapter(Adapter):
        def _decode(self, obj, context, path):
            values = {}

            for idx, enum_value in enumerate(enum_class):
                if idx > 0:
                    mask = 1 << idx - 1
                    values[enum_value] = (obj & mask) > 0

            return values

        def _encode(self, obj, context, path):
            value = 0
            for idx, enum_value in enumerate(enum_class):
                if idx > 0 and obj.get(enum_value, False):
                    value |= 1 << idx - 1

            return value

    return _EnumFlagAdapter


class PaddedCStringAdapter(Adapter):
    def _decode(self, obj, context, path):
        if '\x00' in obj:
            end_of_string = obj.index('\x00')
            return obj[:end_of_string]
        return obj

    def _encode(self, obj, context, path):
        return obj


class BaseCommand(object):
    minimum_version = -1

    @classmethod
    def parse(cls, raw):
        struct = cls._full_struct().parse(raw)
        return cls(
            **struct
        )

    @classmethod
    def _full_struct(cls):
        return Const(cls.name) + cls.format

    def __init__(self, *args, **kwargs):
        for subcon in self.format.subcons:
            if subcon.name and subcon.name[0] != "_":
                if subcon.name not in kwargs:
                    raise Exception('Missing needed value {}'.format(subcon.name))
                else:
                    setattr(self, subcon.name, kwargs[subcon.name])

    def to_bytes(self):
        return self.__class__._full_struct().build(self.__dict__)

    def __repr__(self):
        struct = self.__class__._full_struct().parse(self.to_bytes())
        return '<{} ({}): {}>'.format(
            self.__class__.__name__,
            self.name,
            struct.__repr__()
        )

    def apply_to_state(self, state):
        print('WARN Default implementation of apply_to_state for {}'.format(self.__class__.__name__))
        return state
