#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice


class MockDeviceNso(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='confd', **kwargs)
        self.invalid_command_response = '--------------^\nsyntax error: expecting\n '

    def cisco_config(self, transport, cmd):
        if re.match("services .* endpoint PE1.*", cmd, re.IGNORECASE):
            self.prompt = "admin@ncs(config-endpoint-PE1)# "
            self.set_state(self.transport_handles[transport], 'cisco_config_service_err')
            return True
        elif re.match("services.*", cmd):
            return True

    def juniper_config(self, transport, cmd):
        if re.match("services .* endpoint PE1.*", cmd, re.IGNORECASE):
            self.set_state(self.transport_handles[transport], 'juniper_config_service_err')
            return True
        elif re.match("services.*", cmd):
            return True


def main(args=None):

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
        state = 'connect'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Router'

    md = MockDeviceNso(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
