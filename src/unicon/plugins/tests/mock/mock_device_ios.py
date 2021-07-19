#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper, wait_key

logger = logging.getLogger(__name__)


class MockDeviceIOS(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='ios', **kwargs)
        self.lock_counter = 0

    def enable(self, transport, cmd):
        if cmd == "redundancy force-switchover":
            if len(self.transport_ports) > 1:
                self.set_state(self.transport_handles[transport], 'exec_standby')
                self.state_change_switchover(transport, 'exec_standby', 'enable')
            return True
        elif cmd == "setup_mgmt":
            import signal
            import sys
            def signal_handler(sig, frame):
                self.set_state(self.transport_handles[transport], 'enable')
                print('\n' + self.get_prompt(transport), end='')
            signal.signal(signal.SIGINT, signal_handler)
            return False
        elif 'set config lock count' in cmd:
            self.lock_counter = int(cmd.split()[-1])
            return True
        elif cmd == 'config term':
            if self.lock_counter > 0:
                self.mock_data['enable']['commands']['config term'] \
                    = 'Configuration locked. Ascii config in progress.'
                self.lock_counter -= 1
            else:
                self.mock_data['enable']['commands']['config term'] \
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


class MockDeviceTcpWrapperIOS(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='ios', **kwargs)
        if 'port' in kwargs:
            kwargs.pop('port')
        self.mockdevice = MockDeviceIOS(*args, **kwargs)


def main(args=None):
    logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                        format="%(asctime)s [%(levelname)8s]:  %(message)s")
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
        state = 'exec,exec_standby'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Router'

    if args.ha:
        md = MockDeviceTcpWrapperIOS(hostname=hostname, state=state)
        md.run()
    else:
        md = MockDeviceIOS(hostname=hostname, state=state)
        md.run()


if __name__ == "__main__":
    main()
