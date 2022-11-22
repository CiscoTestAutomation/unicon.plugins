__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import re
import sys
import termios
import logging
import argparse

from unicon.mock.mock_device import MockDevice, wait_key

logger = logging.getLogger(__name__)


class MockDeviceAsa(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='asa', **kwargs)

    def version_more(self, transport, cmd):
        # prompt = self.get_prompt(transport)
        # print(prompt, end="", flush=True)

        while True:
            key = wait_key()
            if key in ['\x04', ' ', '\r', '\n', 'q']:
                break
        if key == ' ':
            self.set_state(0,'asa_enable_more')
            print('\x08 \x08' * 16, end='')
            self.command_handler(transport, ' ')
        return True


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('-d', action='store_true', help='Debug')
        parser.add_argument('--hostname', help='Device hostname (default: ASA')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    else:
        state = 'asa_disable'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'ASA'

    md = MockDeviceAsa(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
