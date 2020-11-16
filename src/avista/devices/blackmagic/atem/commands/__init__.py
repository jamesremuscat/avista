from recordclass import RecordClass
import inspect
import struct
import txaio

from .config import *

COMMAND_LIST = {
    b'_ver': Version,
    b'_pin': ProductName,
    b'_top': [
        [7, TopologyV7],
        [2.28, TopologyV8],
        [2.30, TopologyV811]
    ]
}


log = txaio.make_logger()


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
            log.debug(
                'Command {cmd} not recognised for version {ver}',
                cmd=command_type,
                ver=self._version
            )
