from avista.core import expose
from avista.devices.net import NetworkDevice, NotConnectedException
from twisted.protocols.basic import LineOnlyReceiver


class Messages(object):
    CONNECTION_STATE = 'hyperdeck.connection'
    TRANSPORT_STATE = 'hyperdeck.transport'
    SLOT_STATE = 'hyperdeck.slots'
    CLIPS_STATE = 'hyperdeck.clips'


class InvalidArgumentException(Exception):
    pass


class HyperDeckProtocol(LineOnlyReceiver):

    def __init__(self, device):
        self.device = device
        self._multiline_buffer = []
        self._multiline_mode = False

    def connectionMade(self):
        self.device.log.info('Connected to remote HyperDeck device')
        # Get async updates on HyperDeck state...
        self.sendLine(b'notify: transport: true slot: true')
        # ...and get current state data too
        self.sendLine(b'slot info')
        self.sendLine(b'transport info')
        self.sendLine(b'disk list')

    def lineReceived(self, line):
        if self._multiline_mode:
            if len(line) > 0:
                self._multiline_buffer.append(line.decode('utf-8'))
            else:
                self._handle_message(self._multiline_buffer)
                self._multiline_buffer.clear()
                self._multiline_mode = False
        else:
            if len(line) > 0 and line[-1] == 58:  # 58 == :
                self._multiline_mode = True
                self._multiline_buffer.append(line.decode('utf-8'))
            else:
                self._handle_message([line.decode('utf-8')])

    def _handle_message(self, lines):
        msg_code = lines[0][0:3]
        lines[0] = lines[0][4:]
        payload = {}
        if len(lines) > 1:
            for line in lines[1:]:
                if ': ' in line:
                    key, value = line.split(': ')
                    payload[key] = value

        handler_method_name = "_recv_{}".format(msg_code)
        if hasattr(self.device, handler_method_name) and callable(getattr(self.device, handler_method_name)):
            getattr(self.device, handler_method_name)(payload, lines)
        else:
            self.device.log.warn("Unhandled packet type {code}: {line1} {payload}", code=msg_code, line1=lines[0], payload=payload)


# Mapping functions from textual state message to rich objects
def _bool(string):
    if string == "true":
        return True
    return False


def _int(string):
    if string == "none":
        return None
    try:
        return int(string)
    except ValueError:
        return string


def _map_and_store_state(store, new_state, mapping={}):
    for param, value in new_state.items():
        store[param] = mapping.get(param, lambda a: a)(value)


class HyperDeck(NetworkDevice):
    default_port = 9993

    def __init__(self, config):
        super().__init__(config)
        self._state = {
            'connection': {},
            'slots': {},
            'transport': {},
            'clips': {}
        }

    def create_protocol(self):
        return HyperDeckProtocol(self)

    def send(self, line):
        if self.get_protocol():
            self.get_protocol().sendLine(line.encode('utf-8'))
        else:
            raise NotConnectedException()

    def _recv_200(self, payload, raw):
        pass  # 200 is 'OK'

    def _recv_500(self, payload, raw):
        _map_and_store_state(
            self._state['connection'],
            payload
        )
        self.broadcast_device_message(
            Messages.CONNECTION_STATE,
            self._state['connection'],
            retain=True
        )

    def _recv_208(self, payload, raw):
        mapping = {
            'clip id': _int,
            'loop': _bool,
            'single clip': _bool,
            'speed': _int,
            'slot id': _int,
            'active slot': _int
        }
        _map_and_store_state(
            self._state['transport'],
            payload,
            mapping
        )
        self.broadcast_device_message(
            Messages.TRANSPORT_STATE,
            self._state['transport'],
            retain=True
        )

    def _recv_508(self, payload, raw):
        # Device-initiated version of 208
        self._recv_208(payload, raw)

    def _recv_202(self, payload, raw):
        slot = int(payload.get('slot id', -1))
        if slot >= 0:
            slot_dict = self._state['slots'].setdefault(slot, {})
            _map_and_store_state(
                slot_dict,
                payload,
                {
                    'recording time': _int,
                    'slot id': _int
                }
            )
            self.broadcast_device_message(
                Messages.SLOT_STATE,
                self._state['slots'],
                retain=True
            )

    def _recv_502(self, payload, raw):
        # Device-initiated version of 202
        self._recv_202(payload, raw)

    def _recv_206(self, payload, raw):
        slot = int(payload.get('slot id', -1))
        if slot:
            listing = []

            for line in raw[2:]:
                idx, data = line.split(': ')
                parts = data.split(' ')
                duration = parts.pop()
                video_format = parts.pop()
                file_format = parts.pop()
                name = ' '.join(parts)

                listing.append({
                    'id': idx,
                    'name': name,
                    'file_format': file_format,
                    'video_format': video_format,
                    'duration': duration
                })

            self.broadcast_device_message(
                Messages.CLIPS_STATE,
                self._state['clips'],
                retain=True
            )

    @expose
    def play(self, single_clip=None, speed=None, loop=None):
        '''
Play from the current point of the timeline, at the specified speed.

If `single_clip` is True, then playback will stop (or loop) at the end
of the current clip.

If `loop` is True then playback will loop at the end of the current
timeline (or clip), else it will stop.
        '''
        if single_clip is None and speed is None and loop is None:
            self.send('play')
        else:
            cmd = 'play: '
            if single_clip is not None:
                cmd += 'single clip: {} '.format('true' if single_clip else 'false')
            if speed is not None:
                cmd += 'speed: {} '.format(speed)
            if loop is not None:
                cmd += 'loop: {} '.format('true' if loop else 'false')
            self.send(cmd.strip())

    @expose
    def record(self, clip_name=None):
        if clip_name:
            self.send('record: name: {}'.format(clip_name))
        else:
            self.send('record')
        self._state['transport']['status'] = 'record'  # We don't otherwise get notified of this
        self.broadcast_device_message(
            Messages.TRANSPORT_STATE,
            self._state['transport'],
            retain=True
        )

    @expose
    def stop(self):
        self.send('stop')
        self._state['transport']['status'] = 'stop'
        self.broadcast_device_message(
            Messages.TRANSPORT_STATE,
            self._state['transport'],
            retain=True
        )

    @expose
    def select_slot(self, slot_id):
        if slot_id in [1, 2]:
            self.send('slot select: slot id: {}'.format(slot_id))
            self.refresh_clips_list()
        else:
            raise InvalidArgumentException('Slot {} does not exist'.format(slot_id))

    @expose
    def refresh_clips_list(self):
        self.send('disk list')

    @expose
    def goto_clip(self, clip_id):
        self.send('goto: clip id: {}\r\n'.format(clip_id))

    @expose
    def next_clip(self):
        self.goto_clip('+1')

    def prev_clip(self):
        self.goto_clip('-1')
