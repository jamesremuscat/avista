# avista: Networked audio-visual control

## Introduction

`avista` is a system for controlling audio-visual devices over a network. A
central router orchestrates communication between devices and clients, both of
which can exist anywhere on a network (or even the Internet, if you want).

`avista` uses [WAMP](https://wamp-proto.org/) as its underlying technology.
Clients can _subscribe_ to state updates from devices, as well as make RPC calls
to exposed methods on those devices. While `avista` is written in Python, the
language-agnosticity of WAMP means that clients and even other devices can be
written in any language.

## Device support

A minimal set of devices are supported, but you can write your own too.

- USB-serial relay cards such as KMTronic or ICStation;
- Blackmagic ATEM
- Blackmagic HyperDeck
- VISCA PTZ camera control over serial
- Generic serial and TCP devices

### Ecosystem

  `avista` includes some "ecosystem" devices that warrant special cases:

- The **device manager** maintains a listing of all currently-available
  devices, as well as a machine-discoverable description of its public interface
  methods. All `avista` configurations should include a device manager.
- **System power** is treated specially, to allow devices to react to the power
  being switched on or off. For example, network devices will disconnect prior
  to power-off and reconnect after power-on.

## Configuring an avista network

The heart of an `avista` network is a WAMP router such as
[Crossbar](https://www.crossbar.io/) (example configuration provided in
`examples/crossbar`). It's possible to specify a list of devices within the
Crossbar configuration, but devices can also be run independently, on
separate machines on the network and even ephemerally.

Device definitions live in the `components` section of the Crossbar config
file and look like this:

```json
{
  "type": "class",
  "realm": "realm1",
  "classname": "avista.devices.visca.VISCACamera",
  "extra": {
      "name": "Camera1",
      "port": "/dev/ttyUSB0"
  }
}
```

`type` should always be `class`, and `realm` should match one of the realms
defined earlier on in the configuration. `classname` should point to a
subclass of `avista.core.Device`.

You **must** specify an `extras` object which **must** have a realm-unique
device `name`; this will be used to identify devices. Other options in `extras`
will depend on the specific device type: here, we specify the path to a serial
port for communication with the camera. You may specify `"alwaysPowered": true`
for devices that do not get turned off with the system power; these devices will
not respond to power on/off events.

You only need to include devices here if you want them to run within the
Crossbar router process; this is convenient but there's no requirement to do
so. Devices can be run on any machine with network access to the Crossbar
router, and without the need to specify a configuration centrally.

## Running devices outside of the router

The easiest way to run separate devices is through the `avista-device` command:

```bash
$ avista-device -n MyDeviceName \
  -o option1=value1 -o option2=value2 \
  -r ws://router:8080/ws \
  avista.devices.SomeDeviceClass
```

See `avista-device --help` for a full list of options.

## Connecting clients

A system joining an `avista` network to issue commands to devices, or to view
their current state, is a _client_. This could be a user interface, or an
automated process, or something else.

Connection and authentication are all handled by Crossbar. The example config
provided gives full permission to all connected clients and should only be
used in fully-trusted environments! (TODO: devices should have a separate set
of permissions to clients)

Clients use the WAMP `subscribe` and `call` mechanisms to communicate with
`avista` devices.

### High-level

To join an `avista` network, clients

- Join the WAMP realm, authenticating if configured to be necessary
- Subscribe to `avista.infrastructure.DeviceListing` to receive a list of
  active devices and their _manifests_ (a description of available methods).
- Subscribe to `avista.infrastructure.SystemPowerState` to determine the current
  state of system power.
- Subscribe to the device topics for those devices you're interested in.
- Call methods on devices.

### The `infrastructure` topic

The `avista.infrastructure` topic (along with sub-topics) is used for
system orchestration.

Subscribing to `avista.infrastructure/DeviceListing` will mean clients will
receive an updated device list every time devices are started or stopped. (Be
sure to include retained messages in your subscription to immediately receive
the most recent list.)

A device listing looks like this:

```json
{
    'power': {
        'power_off': {
            'args': [],
            'varargs': None,
            'keywords': None,
            'defaults': None,
            'doc': None
        },
        'power_on': {
            'args': [],
            'varargs': None,
            'keywords': None,
            'defaults': None,
            'doc': None
        }
    },
    'ATEM': {
        'perform_cut': {
            'args': ['me'],
            'varargs': None,
            'keywords': None,
            'defaults': (0, ),
            'doc': None
        }
    }
}
```

Here we see two devices, `power` and `ATEM` - note these names are
case-sensitive. The `power` device has two methods, `power_off` and `power_on`,
neither of which take any arguments. The `ATEM` device has a method
`perform_cut` which takes an optional `me` argument - if not specified, the
default is `0`. `doc`, if present, is a human-readable description of the
method.

`avista.infrastructure/SystemPowerState` will give you the current state of the
system power: one of `off`, `on`, `turning_off` and `turning_on`, which are
hopefully self-explanatory.

### Device state topics

Each device will broadcast its state to an individual topic (some devices
use subtopics) of the form:

`avista.devices.<device name>[/subtopic]`

So to receive updates on the `power` device, subscribe to
`avista.devices.power` (again, including retained messages to immediately
receive the current state).

## Crossbar miscellany

There's a [bug in Crossbar's handling of retained events and prefix-matched
subscriptions](https://github.com/crossbario/crossbar/issues/1242), which means
you can't successfully do the following:

```python
session.subscribe(  # XXX THIS DOES NOT WORK
  some_handler_method,
  'avista.infrastructure',
  SubscribeOptions(
    get_retained=True,
    match='prefix'
  )
)
```

Instead you must do this:

```python
session.subscribe(
  some_handler_method,
  'avista.infrastructure/SystemPowerState',
  SubscribeOptions(get_retained=True)
)
session.subscribe(
  some_handler_method,
  'avista.infrastructure/DeviceListing',
  SubscribeOptions(get_retained=True)
)
# Repeat for any other subtopics
```

Each message consists of a `type` and `data`, so your `some_handler_method` can
work out what sort of message it received. (Or you could have separate handler
methods.)
