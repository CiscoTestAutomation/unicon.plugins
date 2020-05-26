__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import re
import sys
import termios
import logging
import argparse

from unicon.mock.mock_device import MockDevice, wait_key

logger = logging.getLogger(__name__)


class MockDeviceVos(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='vos', **kwargs)

    def press_enter(self, transport, cmd):
        while True:
            key = wait_key()
            if key in ['\x04', ' ', '\r', '\n', 'q']:
                break
        if key == ' ':
            self.set_state(0,'press_enter2')
        elif key == 'q':
            self.set_state(0,'vos_exec')
            print()
        else:
            print()
        return True

    def press_enter2(self, transport, cmd):
        self.press_enter(transport, cmd)
        self.set_state(0,'press_enter3')
        return True

    def press_enter3(self, transport, cmd):
        self.press_enter(transport, cmd)
        self.set_state(0,'vos_exec')
        print()
        return True

    def run(self):
        """ Runs the mock device on standard input/output """
        self.add_port(0, self.states[0])
        self.add_transport(sys.stdout, 0)

        while True:
            self.state_handler(sys.stdout)

            prompt = self.transport_ports[
                self.transport_handles[sys.stdout]
            ]['prompt']

            prompt = prompt.replace('ESC', '\x1b')

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
        parser.add_argument('--hostname', help='Device hostname (default: Router')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    else:
        state = 'vos_connect'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Router'

    md = MockDeviceVos(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
