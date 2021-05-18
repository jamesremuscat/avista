from construct import Adapter, Const
from avista.devices.blackmagic.atem.constants import VideoSource

import copy


def EnumAdapter(enum_class):
    class _EnumAdapter(Adapter):
        def _decode(self, obj, context, path):
            return enum_class(obj)

        def _encode(self, obj, context, path):
            return obj.value if obj else None
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
        if isinstance(obj, bytes):
            if b'\x00' in obj:
                end_of_string = obj.index(b'\x00')
                return obj[:end_of_string].decode('utf-8')
            return obj.decode('utf-8')
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
                    self.handle_missing_value(subcon.name)
                else:
                    setattr(self, subcon.name, kwargs[subcon.name])

    def handle_missing_value(self, value_name):
        raise Exception('Missing needed value {}'.format(value_name))

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


class BaseSetCommand(BaseCommand):
    def handle_missing_value(self, value_name):
        pass


def clone_state_with_key(state, key, default=None):
    new_state = copy.copy(state)
    new_state[key] = copy.copy(state.get(key, default or {}))

    return (new_state, new_state[key])


def recalculate_synthetic_tally(state):
    new_state, tally = clone_state_with_key(state, 'tally')

    tally['by_me'] = {}

    for idx, me in new_state.get('mes', {}).items():
        this_me = {}

        if me.get('preview'):
            this_me.setdefault(me['preview'], {})['preview'] = True

            if me['preview'] == VideoSource.SUPER_SOURCE:
                for sssrc in _get_all_supersource_sources(new_state.get('super_source', {})):
                    this_me.setdefault(sssrc, {})['preview'] = True

        if me.get('program'):
            this_me.setdefault(me['program'], {})['program'] = True

            if me['program'] == VideoSource.SUPER_SOURCE:
                for sssrc in _get_all_supersource_sources(new_state.get('super_source', {})):
                    this_me.setdefault(sssrc, {})['program'] = True

        # Also consider any active upstream keyers:
        for keyer in me.get('keyers', {}).values():
            if keyer.get('on_air'):
                if keyer.get('fill_source'):
                    this_me.setdefault(keyer['fill_source'], {})['program'] = True
                if keyer.get('key_source'):
                    this_me.setdefault(keyer['key_source'], {})['program'] = True

                if VideoSource.SUPER_SOURCE in [keyer.get('fill_source'), keyer.get('key_source')]:
                    for sssrc in _get_all_supersource_sources(new_state.get('super_source', {})):
                        this_me.setdefault(sssrc, {})['program'] = True

        # If we're transitioning, we need to consider both program and preview live
        if me.get('transition'):
            if me['transition'].get('next'):
                transition = me['transition']

                if transition.get('position', {}).get('in_transition'):
                    tie = transition.get('next', {})

                    if tie.get('background') and me.get('preview'):
                        this_me.setdefault(me['preview'], {})['program'] = True

                    for index, keyer in enumerate(me.get('keyers', {}).values()):
                        key_tie = "key_{}".format(index + 1)
                        if tie.get(key_tie):
                            if keyer.get('fill_source'):
                                this_me.setdefault(keyer['fill_source'], {})['program'] = True
                            if keyer.get('key_source'):
                                this_me.setdefault(keyer['key_source'], {})['program'] = True

                            if VideoSource.SUPER_SOURCE in [keyer.get('fill_source'), keyer.get('key_source')]:
                                for sssrc in _get_all_supersource_sources(new_state.get('super_source', {})):
                                    this_me.setdefault(sssrc, {})['program'] = True

        for source in new_state.get('sources', []):
            this_source = this_me.setdefault(source, {})

            if 'preview' not in this_source:
                this_source['preview'] = False
            if 'program' not in this_source:
                this_source['program'] = False

        tally['by_me'][idx] = this_me

    # DSKs always appear on M/E 1 (index 0)
    for dsk in new_state.get('dsks', {}).values():
        dsk_state = dsk.get('state', {})
        if dsk_state.get('on_air') or dsk_state.get('is_transitioning'):
            if dsk.get('fill_source'):
                tally['by_me'][0][dsk['fill_source']]['program'] = True
            if dsk.get('key_source'):
                tally['by_me'][0][dsk['key_source']]['program'] = True

            if VideoSource.SUPER_SOURCE in [dsk.get('fill_source'), dsk.get('key_source')]:
                for sssrc in _get_all_supersource_sources(new_state.get('super_source', {})):
                    tally['by_me'][0][sssrc]['program'] = True

    return new_state


def _get_all_supersource_sources(ssrc):
    sources = []

    if ssrc.get('fill_source'):
        sources.append(ssrc['fill_source'])
    if ssrc.get('key_source') and ssrc.get('foreground'):
        sources.append(ssrc['key_source'])

    for box in ssrc.get('boxes', []):
        if box.get('enabled'):
            sources.append(box['source'])

    return sources
