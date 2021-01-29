from collections import defaultdict
from recordclass import RecordClass
import inspect
import struct
import txaio

from .base import BaseCommand
from .audio import *
from .config import *
from .macro import *
from .media import *
from .settings import *


log = txaio.make_logger()


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


COMMAND_LIST = defaultdict(list)

for command_class in get_all_subclasses(BaseCommand):
    if hasattr(command_class, 'name'):
        log.debug(
            'Discovered command: {name} (version {ver})'.format(
                name=command_class.name,
                ver=command_class.minimum_version
            )
        )
        name = command_class.name
        COMMAND_LIST[name].append([
            command_class.minimum_version,
            command_class
        ])
    else:
        raise Exception('Command class without defined name: {}'.format(command_class))


class CommandParser(object):
    def __init__(self):
        self._version = None

    def parse_commands(self, payload):
        commands = []
        if len(payload) > 2:
            while len(payload) > 0:
                size = struct.unpack('!H', payload[0:2])[0]
                command = payload[4:size]
                payload = payload[size:]

                if int.from_bytes(command[:4], 'big') & 0xFFFFFFFF:
                    cmd = self.parse_command(command)
                    if cmd:
                        commands.append(cmd)
                        if isinstance(cmd, Version):
                            self._version = float(
                                '{}.{}'.format(
                                    cmd.major,
                                    cmd.minor
                                )
                            )
                            log.info(
                                'Set ATEM protocol version to {ver}',
                                ver=self._version
                            )
        return commands

    def parse_command(self, payload):
        command_type = payload[:4]

        cmd_class = COMMAND_LIST.get(command_type)

        if inspect.isclass(cmd_class):
            return cmd_class.parse(payload)
        elif isinstance(cmd_class, list):
            if self._version is None:
                return cmd_class[-1][1].parse(payload)
            else:
                version_options = sorted(cmd_class, key=lambda o: -o[0])

                res = next(
                    val for val in version_options if val[0] <= self._version
                )
                return res[1].parse(payload)
        else:
            log.warn(
                'Command {cmd} not recognised for version {ver}: {full}',
                cmd=command_type,
                ver=self._version,
                full=payload
            )
