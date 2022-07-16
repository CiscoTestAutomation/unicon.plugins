#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper, wait_key

logger = logging.getLogger(__name__)


class MockDeviceAOS(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='aos', **kwargs)
        self.lock_counter = 0

    def enable(self, transport, cmd):
        if cmd == 'configure terminal':
            if self.lock_counter > 0:
                self.mock_data['exec']['commands']['configure terminal'] \
                    = 'Configuration locked. Ascii config in progress.'
                self.lock_counter -= 1
            else:
                self.mock_data['exec']['commands']['configure terminal'] \
                    = {'new_state': 'config'}

    def ping3_count(self, transport, cmd):
        logger.debug("Ping count '%s'" % cmd)
        if cmd != '5':
            self.valid_commands(['5'], transport)
        self.set_state(self.transport_handles[transport], 'ping3_size')
        return True

    def ping3_size(self, transport, cmd):
        logger.debug("Ping size '%s'" % cmd)
        if cmd != '1500':
            self.valid_commands(['1500'], transport)
        self.set_state(self.transport_handles[transport], 'ping3_timeout')
        return True

    def ping3_timeout(self, transport, cmd):
        logger.debug("Ping timeout '%s'" % cmd)
        if cmd != '2':
            self.valid_commands(['2'], transport)
        self.set_state(self.transport_handles[transport], 'ping3_extend')
        return True

    def config(self, transport, cmd):
        m = re.match(r'\s*hostname (\S+)', cmd)
        if m:
            self.hostname = m.group(1)
            return True


class MockDeviceTcpWrapperAOS(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='aos', **kwargs)
        if 'port' in kwargs:
            kwargs.pop('port')
        self.mockdevice = MockDeviceAOS(*args, **kwargs)


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--ha', action='store_true', help='HA mode')
        parser.add_argument('--hostname', help='Device hostname (default: Router')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    else:
        state = 'enable'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Router'


    md = MockDeviceAOS(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
