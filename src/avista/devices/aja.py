from avista.core import Device, expose
from enum import Enum
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.error import AlreadyCalled
from twisted.web.client import Agent, HTTPConnectionPool

import time
import treq


class RecordingState(Enum):
    IDLE = 1
    RECORDING = 2


POLL_INTERVAL = 3


class Helo(Device):
    def __init__(self, config):
        super().__init__(config)
        self.host = config.extra.get('host')
        self.always_powered = config.extra.get('alwaysPowered')

        self._api_root = f'http://{self.host}/config?'

        self._client = treq.client.HTTPClient(
            Agent(
                reactor,
                pool=HTTPConnectionPool(reactor, persistent=True)
            )
        )

        self._state = {}
        self._connectionID = None

        self._pollCall = None

        self._shouldPoll = False

        if self.always_powered:
            self.after_power_on()

    def after_power_on(self):
        self._shouldPoll = True
        d = Deferred.fromCoroutine(self._start_polling())
        spo = super().after_power_on

        # On error try again in 10 seconds
        def handle_err(e):
            self.log.error('Error connecting to Helo {host}: {e}', host=self.host, e=e)
            reactor.callLater(10, self.after_power_on)

        d.addCallbacks(
            lambda _: spo(),
            handle_err
        )

    def before_power_off(self):
        self._shouldPoll = False
        self._stop_polling()
        return super().before_power_off()

    async def _start_polling(self):
        url = f'{self._api_root}action=connect'
        state = await self._client.get(url)
        state_obj = await treq.json_content(state)
        self._connectionID = state_obj['connectionid']
        config_events = state_obj['configevents']
        for event in config_events:
            for param, value in event.items():
                self._handle_param_update(param, value)
        self._broadcast_state()
        if self._shouldPoll:
            self._pollCall = reactor.callLater(POLL_INTERVAL, self._do_poll)
        return True

    def _do_poll(self):
        return Deferred.fromCoroutine(self._do_poll_async())

    async def _do_poll_async(self):
        try:
            if self._connectionID is not None:
                url = f'{self._api_root}action=wait_for_config_events&connectionid={self._connectionID}&_={time.time()}'
                state = await self._client.get(url)
                state_obj = await treq.json_content(state)
                for event in state_obj:
                    if 'param_type' in event:
                        value = event['str_value'] if event['param_type'] == '12' else event['int_value']  # ...which also happens to be a string, thanks AJA
                        self._handle_param_update(event['param_id'], value)
                self._broadcast_state()
        except Exception as e:
            self.log.error('Error polling Helo {host}: {e}', host=self.host, e=e)
        self._pollCall = reactor.callLater(POLL_INTERVAL, self._do_poll)

    def _stop_polling(self):
        if self._pollCall:
            try:
                self._pollCall.cancel()
            except AlreadyCalled:
                pass
        self._connectionID = None

    def _handle_param_update(self, param_name, value):
        key = param_name.replace('eParamID_', '')
        self._state[key] = value

    def _broadcast_state(self):
        self.broadcast_device_message(
            'state',
            data=self._state,
            retain=True
        )

    @expose
    async def start_recording(self):
        url = f'{self._api_root}action=set&paramid=eParamID_ReplicatorCommand&value=1'
        await treq.get(url)

    @expose
    async def stop_recording(self):
        url = f'{self._api_root}action=set&paramid=eParamID_ReplicatorCommand&value=2'
        await treq.get(url)

    @expose
    async def start_streaming(self):
        url = f'{self._api_root}action=set&paramid=eParamID_ReplicatorCommand&value=3'
        await treq.get(url)

    @expose
    async def stop_streaming(self):
        url = f'{self._api_root}action=set&paramid=eParamID_ReplicatorCommand&value=4'
        await treq.get(url)

    @expose
    async def toggle_link(self):
        current_value = int(self._state.get('LinkStartStop', 0))
        url = f'{self._api_root}action=set&paramid=eParamID_LinkStartStop&value={1 - current_value}'
        await treq.get(url)
