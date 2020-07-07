__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import re
import sys
import termios
import logging
import argparse

from unicon.mock.mock_device import MockDevice

logger = logging.getLogger(__name__)


class MockDeviceVos(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='vos', **kwargs)


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
