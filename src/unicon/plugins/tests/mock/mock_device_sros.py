#!/usr/bin/env python3

import logging
import argparse

from unicon.mock.mock_device import MockDevice

logger = logging.getLogger(__name__)


class MockDeviceSROS(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='sros', **kwargs)
        self.invalid_command_response = "Error: Bad command "


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--hostname', help='Device hostname (default: Router')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    state = args.state or 'connect_ssh'
    hostname = args.hostname or 'Router'
    md = MockDeviceSROS(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
