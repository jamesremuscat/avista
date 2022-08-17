from avista.core import Device
from netaudio.dante.browser import DanteBrowser

import asyncio


DEFAULT_REFRESH_INTERVAL = 10


class Dante(Device):
    '''
    A device to interface with a Dante audio network.

    This device requires asyncio (ensure that `AVISTA_USE_ASYNCIO` is set) and
    cannot be used directly in the Crossbar config file as a result: use the
    `avista-device` command, in a systemd service if you would like.
    '''
    def __init__(self, config):
        super().__init__(config)
        self._state = {
            'devices': {}
        }
        self._devices = {}
        self._browser = DanteBrowser(mdns_timeout=1.5)

        self._refresh_interval = config.extra.get('refresh_interval', DEFAULT_REFRESH_INTERVAL)

        self._refresh_lock = asyncio.Lock()

        self.refresh_device_list()

    def refresh_device_list(self):
        task = asyncio.create_task(self._refresh_device_list_async())
        task.add_done_callback(self._handle_device_list)

    async def _refresh_device_list_async(self):
        async with self._refresh_lock:
            self._devices = await self._browser.get_devices()

            for device in self._devices.values():
                await device.get_controls()

            devices_json = {
                k: v.to_json() for k, v in self._devices.items()
            }

            # Map from netaudio's objects to simplified dicts
            for device in devices_json.values():
                device['subscriptions'] = list(map(lambda s: s.to_json(), device['subscriptions']))
                device['channels']['transmitters'] = {
                    k: v.to_json() for k, v in device['channels']['transmitters'].items()
                }
                device['channels']['receivers'] = {
                    k: v.to_json() for k, v in device['channels']['receivers'].items()
                }
                del device['services']

            return devices_json

    def _handle_device_list(self, devices):
        self._state['devices'] = devices.result()

        self.broadcast_device_message(
            'devices',
            self._state['devices']
        )

        loop = asyncio.get_event_loop()
        loop.call_later(10, self.refresh_device_list)
