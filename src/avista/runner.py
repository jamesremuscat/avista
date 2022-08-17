from argparse import ArgumentParser
from autobahn.rawsocket.util import parse_url as parse_rs_url
from autobahn.websocket.util import parse_url as parse_ws_url
from twisted.internet.ssl import CertificateOptions

import importlib
import inspect
import os
import sys
import txaio

from .core import Device


def _parse_args(args):
    parser = ArgumentParser()

    parser.add_argument(
        '-n', '--name',
        required=True,
        help='Name of the device'
    )

    parser.add_argument(
        '-o', '--option',
        action='append',
        help='Additional device options, specified as `option=value` pairs'
    )

    parser.add_argument(
        '-r', '--router',
        default=None,
        help='URL of avista Crossbar router to connect to'
    )

    parser.add_argument(
        '--realm',
        default='avista',
        help='WAMP realm to join'
    )

    parser.add_argument(
        '--debug',
        default=False,
        action='store_true'
    )

    parser.add_argument('device_class')

    return parser.parse_args(args)


def _import_device_class(device_class):
    parts = device_class.split('.')
    module_name = '.'.join(parts[0:-1])
    module = importlib.import_module(module_name)
    return getattr(module, parts[-1])


def _endpoint_and_type_from_url(url):
    if url[0:2] == 'ws':
        is_secure, host, port, resource, path, params = parse_ws_url(url)

        endpoint = {
            'type': 'tcp',
            'host': host,
            'port': port,
            'tls': is_secure
        }
        type = 'websocket'

    elif url[0:2] == 'rs':
        _, host, path = parse_rs_url(url)
        type = 'rawsocket'
        if host == 'unix':
            endpoint = {
                'type': 'unix',
                'path': path
            }
        else:
            endpoint = {
                'type': 'tcp',
                'host': host,
                'port': path
            }

    else:
        raise RuntimeError('Unknown router URL protocol: {} (should be ws://, wss:// or rs://)'.format(url))

    if is_secure and endpoint['type'] == 'tcp' and os.name == 'nt':
        # Disable SSL verification on Windows because Windows
        endpoint['tls'] = CertificateOptions(verify=False)

    return (endpoint, type)


def run():
    args = _parse_args(sys.argv[1:])

    router_url = args.router or os.environ.get('AVISTA_ROUTER_URL')

    if not router_url:
        raise RuntimeError('No Crossbar router URL specified and AVISTA_ROUTER_URL not set. Cannot continue.')

    if os.environ.get('AVISTA_USE_ASYNCIO'):
        from autobahn.asyncio.component import Component, run as autobahn_run
    else:
        from autobahn.twisted.component import Component, run as autobahn_run

    device_class = _import_device_class(args.device_class)
    if not inspect.isclass(device_class) or not issubclass(device_class, Device):
        raise RuntimeError(
            'Specified class {} is not an avista device class'.format(
                args.device_class
            )
        )

    endpoint, type = _endpoint_and_type_from_url(router_url)

    extra = {
        'name': args.name
    }

    if args.debug:
        txaio.start_logging(level='debug')

    if args.option:
        for optval in args.option:
            if '=' not in optval:
                raise RuntimeError('Incorrectly specified option: {}'.format(optval))
            option, value = optval.split('=')
            extra[option] = value

    component = Component(
        extra=extra,
        realm=args.realm,
        session_factory=device_class,
        transports=[
            {
                'url': router_url,
                'type': type,
                'endpoint': endpoint,
                'max_retry_delay': 30
            }
        ]
    )

    autobahn_run([component])
