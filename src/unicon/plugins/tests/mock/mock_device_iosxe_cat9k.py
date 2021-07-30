#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)


class MockDeviceIOSXECat9k(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="iosxe", **kwargs)
        self.config_lock_counter = 0
        self.files_on_flash = []

    def cat9k_ha_active_enable_reload_proceed(self, transport, cmd):
        if 'prompt' in self.transport_ports[self.transport_handles[transport]]:
            prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
            if cmd == "" and prompt == 'Proceed with reload? [confirm]':
                prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
                if len(self.transport_ports) > 1 :
                    self.state_change_switchover(
                        transport, 'cat9k_ha_active_enable_reload', 'cat9k_ha_active_enable')
                return True

    def cat9k_ha_active_config_redundancy_mc(self, transport, cmd):
        if cmd == 'standby console enable':
            logger.info(self.transport_ports)
            handles = [h for h in self.transport_handles if h != transport]
            logger.info(handles)
            self.set_state(self.transport_handles[handles[0]],
                           'cat9k_ha_standby_disable')


class MockDeviceTcpWrapperIOSXECat9k(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='iosxe', **kwargs)

        if 'port' in kwargs:
            kwargs.pop('port')

        self.mockdevice = MockDeviceIOSXECat9k(*args, **kwargs)



def main(args=None):
    logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                        format="%(asctime)s [%(levelname)8s]:  %(message)s")
    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--ha', action='store_true', help='HA mode')
        parser.add_argument('--hostname', help='Device hostname (default: Switch')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    elif args.ha:
        state = 'asr_exec,asr_exec_standby'
    else:
        state = 'asr_exec'
    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Switch'

    if args.ha:
        md = MockDeviceTcpWrapperIOSXE(hostname=hostname, state=state)
        md.run()
    else:
        md = MockDeviceIOSXE(hostname=hostname, state=state)
        md.run()


if __name__ == "__main__":
    main()
