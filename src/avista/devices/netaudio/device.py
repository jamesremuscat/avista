from avista.core import Device, expose
from netaudio.dante.browser import DanteBrowser

import asyncio


DEFAULT_REFRESH_INTERVAL = 10


class DeviceNotFound(Exception):
    pass


def device_by_name(devices, device_name):
    try:
        return next(
            filter(
                lambda d: d.name == device_name,
                devices.values(),
            )
        )
    except StopIteration:
        return None


def channel_by_name(channels, channel_name):
    try:
        return next(
            filter(
                lambda c: c.name == channel_name,
                channels.values(),
            )
        )
    except StopIteration:
        return None


def channel_by_number(channels, channel_number):
    try:
        return next(
            filter(
                lambda c: c.number == channel_number,
                channels.values(),
            )
        )
    except StopIteration:
        return None


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

    @expose
    async def set_subscription(self, tx_device_name, tx_channel, rx_device_name, rx_channel):
        rx_device = device_by_name(self._devices, rx_device_name)

        if not rx_device:
            raise DeviceNotFound(rx_device_name)

        tx_device = device_by_name(self._devices, tx_device_name)

        if not tx_device:
            raise DeviceNotFound(tx_device_name)

        if type(tx_channel) == int:
            tx_chan = channel_by_number(tx_device.tx_channels, tx_channel)
        else:
            tx_chan = channel_by_name(tx_device.tx_channels, tx_channel)

        if type(rx_channel) == int:
            rx_chan = channel_by_number(rx_device.rx_channels, rx_channel)
        else:
            rx_chan = channel_by_name(rx_device.rx_channels, rx_channel)

        if tx_chan and rx_chan:
            await rx_device.add_subscription(rx_chan, tx_chan, tx_device)
