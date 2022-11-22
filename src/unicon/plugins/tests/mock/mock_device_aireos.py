__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import re
import sys
import termios
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper, wait_key

logger = logging.getLogger(__name__)


class MockDeviceAireos(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='aireos', **kwargs)

    def aireos_press_any_key(self, transport, cmd):
        while True:
            key = wait_key()
            break
        print('\x08' * (len(self.get_prompt(transport))+1), end='')
        self.command_handler(transport, key)
        return True

    def aireos_show_command_with_more(self, transport, cmd):
        return self.aireos_press_any_key(transport, cmd)

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


class MockDeviceTcpWrapperAireos(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='aireos', **kwargs)
        if 'port' in kwargs:
            kwargs.pop('port')
        self.mockdevice = MockDeviceAireos(*args, **kwargs)



def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('-d', action='store_true', help='Debug')
        parser.add_argument('--hostname', help='Device hostname (default: Router')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    else:
        state = 'aireos_disable'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Cisco Capwap Simulator'

    if args.ha:
        md = MockDeviceTcpWrapperAireos(hostname=hostname, state=state)
        md.run()
    else:
        md = MockDeviceAireos(hostname=hostname, state=state)
        md.run()


if __name__ == "__main__":
    main()
