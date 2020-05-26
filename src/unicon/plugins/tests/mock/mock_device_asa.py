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

    def run(self):
        """ Runs the mock device on standard input/output """
        self.add_port(0, self.states[0])
        self.add_transport(sys.stdout, 0)

        while True:
            self.state_handler(sys.stdout)

            prompt = self.get_prompt(sys.stdout)

            print(prompt, end="", flush=True)

            cmd = ""
            if self.method_handler(sys.stdout, cmd):
                continue
            else:
                try:
                    while True:
                        key = wait_key()
                        if key in ['\x04']:
                            raise EOFError()
                        if key == '\n':
                            break
                        else:
                            cmd += key

                except EOFError:
                    break

                self.command_handler(sys.stdout, cmd)


def main(args=None):
    logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                        format="%(asctime)s [%(levelname)8s]:  %(message)s")
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
