#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)


class MockDeviceNXOS(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="nxos", **kwargs)
        self.config_lock_counter = 0
        self.files_on_flash = []

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

    def exec(self, transport, cmd):
        if 'set config lock count' in cmd:
            self.config_lock_counter = int(cmd.split()[-1])
            return True
        elif cmd == 'config term':
            if self.config_lock_counter > 0:
                self.mock_data['exec']['commands']['config term'] \
                    = "Configuration mode locked exclusively by user 'unknown' process '13' from terminal '0'. Please try later."
                self.config_lock_counter -= 1
            else:
                self.mock_data['exec']['commands']['config term'] \
                    = {'new_state': 'config'}
        # 'show tech > bootflash:R1_show_tech_20210405T112036168.txt'
        elif re.match(r'show tech.*>', cmd):
            filename = re.sub(r'show tech.*>', '', cmd).strip()
            self.files_on_flash.append(filename)
            return True
        elif cmd == 'dir':
            lines = ['   52429131    Apr 05 08:53:17 2021  ' + f for f in self.files_on_flash]
            self._write('\n'.join(lines), transport)
            self._write('\n\n', transport)
            return True
        elif re.match(r'tar create \S+ gz-compress \S+', cmd):
            m = re.match(r'tar create (\S+) gz-compress \S+', cmd)
            filename = m.group(1) + '.tar.gz'
            self.files_on_flash.append(filename)
            return True
        elif re.match(r'delete \S+', cmd):
            m = re.match(r'delete (\S+)', cmd)
            filename = m.group(1)
            self.files_on_flash.remove(filename)
            return True
        elif re.match(r'copy bootflash:\S+ scp:\S+ vrf \S+', cmd):
            self.set_state(self.transport_handles[transport], 'scp_password')
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
