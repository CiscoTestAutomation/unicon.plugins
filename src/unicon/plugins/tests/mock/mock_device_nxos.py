#!/usr/bin/env python3

import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)


class MockDeviceNXOS(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="nxos",  **kwargs)

    def ha_confirm_reload(self, transport, cmd):
        if 'prompt' in self.transport_ports[self.transport_handles[transport]]:
            prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
            if cmd == "y" and prompt == 'This command will reboot the system. (y/n)?  [n]':
                prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
                if len(self.transport_ports) > 1 :
                    self.state_change_switchover(
                        transport, 'ha_active_console', 'ha_standby_console')
                prompt = self.mock_data['ha_standby_console']['prompt']
                self.get_other_transport(transport).write(prompt.encode())
                return True


class MockDeviceTcpWrapperNXOS(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='nxos', **kwargs)
        if 'port' in kwargs:
            kwargs.pop('port')
        self.mockdevice = MockDeviceNXOS(*args, **kwargs)


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
    elif args.ha:
        state = 'exec,nxos_exec_standby'
    else:
        state = 'exec'
    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'switch'
    if args.ha:
        md = MockDeviceTcpWrapperNXOS(hostname=hostname, state=state)
        md.run()
    else:
        md = MockDeviceNXOS(hostname=hostname, state=state)
        md.run()


if __name__ == "__main__":
    main()
