__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice

logger = logging.getLogger(__name__)


class MockDeviceFxos(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='fxos', **kwargs)

    def fp2k_ftd_exec(self, transport, cmd):
        if cmd == 'exit':
            self.command_handler(transport, cmd)
            sys.exit()

    def fp2k_telnet_escape(self, transport, cmd):
        if cmd == 'q':
            self.command_handler(transport, cmd)
            sys.exit()

    def conn_closed(self, transport, cmd):
        sys.exit()


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('-d', action='store_true', help='Debug')
        parser.add_argument('--hostname', help='Device hostname (default: Firepower')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    else:
        state = 'fxos_exec'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Firepower'

    md = MockDeviceFxos(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
