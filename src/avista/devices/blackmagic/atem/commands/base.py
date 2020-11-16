from construct import Const


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
