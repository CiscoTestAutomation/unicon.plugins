#!/usr/bin/env python3
"""
Module:
    unicon.plugins.tests.mock.mock_device_ironware

Author:
    James Di Trapani <james@ditrapani.com.au> - https://github.com/jamesditrapani

Description:
    Subpackage providing a mock Ironware device for Unit Tests
"""

__author__ = "James Di Trapani <james@ditrapani.com.au>"

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)

class MockDeviceIronWare(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='ironware', **kwargs)


class MockDeviceTcpWrapperIronWare(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='ironware', **kwargs)
        self.mockdevice = MockDeviceIronWare(*args, **kwargs)


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--hostname', help='Device hostname (default: Router')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    state = args.state or 'login,console_standby'
    hostname = args.hostname or 'mlx8'
    md = MockDeviceIronWare(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
