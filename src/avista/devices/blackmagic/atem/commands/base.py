class BaseCommand(object):
    @classmethod
    def parse(cls, raw):
        struct = cls.format.parse(raw)
        return cls(
            **struct
        )

    def __init__(self, *args, **kwargs):
        for subcon in self.format.subcons:
            if subcon.name and subcon.name[0] != "_":
                if subcon.name not in kwargs:
                    raise Exception('Missing needed value {}'.format(subcon.name))
                else:
                    setattr(self, subcon.name, kwargs[subcon.name])

    def to_bytes(self):
        return self.format.build(self.__dict__)

    def __repr__(self):
        struct = self.format.parse(self.to_bytes())
        return '<{} ({}): {}>'.format(
            self.__class__.__name__,
            struct._name.decode('utf-8'),
            struct.__repr__()
        )
