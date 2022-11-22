#!/usr/bin/env python3

import re
import sys
import fnmatch
import logging
import argparse
import datetime
from textwrap import dedent

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper, wait_key

logger = logging.getLogger(__name__)

class MockDeviceIOSXE(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="iosxe", **kwargs)
        self.config_lock_counter = 0
        self.files_on_flash = []
        self.rommon_prompt_count = 1

    def enable_asr(self, transport, cmd):
        if cmd == "redundancy force-switchover":
            if len(self.transport_ports) > 1 :
                self.set_state(self.transport_handles[transport],
                    'asr_exec_standby')
                self.state_change_switchover(
                    transport, 'asr_exec_standby', 'enable_asr')
            return True

    def ha_reload_proceed(self, transport, cmd):
         if 'prompt' in self.transport_ports[self.transport_handles[transport]]:
             prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
             if cmd == "" and prompt == 'Proceed with reload? [confirm]':
                 prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
                 if len(self.transport_ports) > 1 :
                    self.state_change_switchover(
                          transport, 'cat9k_ha_active_console', 'cat9k_ha_standby_console')
                 return True

    def general_enable(self, transport, cmd):
        if 'set config lock count' in cmd:
            self.config_lock_counter = int(cmd.split()[-1])
            return True
        elif cmd == 'config term':
            if self.config_lock_counter > 0:
                self.mock_data['general_enable']['commands']['config term'] \
                    = "Configuration mode is locked by process '484' user 'NETCONF' from terminal '64'. Please try later."
                self.config_lock_counter -= 1
            else:
                self.mock_data['general_enable']['commands']['config term'] \
                    = {'new_state': 'general_config'}
        elif re.match(r'show tech.*\| redirect', cmd):
            filename = re.sub(r'show tech.*\| redirect', '', cmd).strip()
            self.files_on_flash.append(filename)
            return True
        elif cmd == 'dir':
            lines = ['      Directory of flash:/']
            if self.files_on_flash:
                lines += ['   52429131    Apr 05 08:53:17 2021  ' + f for f in self.files_on_flash]
                self._write('\n'.join(lines), transport)
                self._write('\n\n', transport)
                self._write('        11353194496 bytes total (1054248960 bytes free)', transport)
                return True
            else:
                return False
        elif re.match(r'delete \S+', cmd):
            m = re.match(r'delete (\S+)', cmd)
            filename = m.group(1)
            for fn in self.files_on_flash:
                if fnmatch.fnmatch(fn, filename):
                    self.files_on_flash.remove(filename)
            return True
        elif re.match(r'copy flash:\S+ scp:\S+', cmd):
            self.set_state(self.transport_handles[transport], 'scp_password')
            return True
        elif re.match(r'copy http://127.0.0.1:\d+/test.txt flash:', cmd):
            return True
        elif re.match(r'copy test.txt http://127.0.0.1:\d+/R1_test.txt', cmd):
            return True
        elif cmd == 'get terminal position':
            self._write('\x1b[6n', transport)
            sys.stdout.flush()
            wait_key()
            return True
        elif re.match(r'dir flash:/?CRFT_\*', cmd):
            lines = ['   52429131    Apr 05 08:53:17 2021  ' + f for f in self.files_on_flash if 'CRFT_' in f]
            if lines:
                self._write('\n'.join(lines), transport)
                self._write('\n\n', transport)
                return True
            else:
                return False
        elif re.match(r'dir flash:/?BTRACE_\*', cmd):
            lines = ['   52429131    Apr 05 08:53:17 2021  ' + f for f in self.files_on_flash if 'BTRACE_' in f]
            if lines:
                self._write('\n'.join(lines), transport)
                self._write('\n\n', transport)
                return True
            else:
                return False
        elif re.match(r'request platform software trace archive target flash:/.*', cmd):
            output = dedent("""
            Creating archive file [flash:/test.tar.gz]

            Done with creation of the archive file: [flash:/test.tar.gz]
            """)
            self._write(output, transport)
            self._write('\n\n', transport)
            self.files_on_flash.append('test.tar.gz')
            return True
        elif re.match(r'request platform software crft.*', cmd):
            self._write('Successful remote archive of CRFT collection to "/bootflash/test.tar.gz" with checksum 20df732e655aed41522550cc4e6f0329', transport)
            self._write('\n\n', transport)
            self.files_on_flash.append('test.tar.gz')
            return True
        elif re.match('copy flash:/CRFT.*', cmd):
            self._write('537450 bytes copied in 3.021 secs (177905 bytes/sec)\n', transport)
            return True
        elif re.match(r"verify /md5 (.*)", cmd):
            m = re.match(r"verify /md5 (.*)", cmd)
            filename = m.group(1)
            output = dedent("""

            .............Done!

            verify /md5 ({}) = d8e8fca2dc0f896fd7cb4cb0031ba249
            """.format(filename))
            self._write(output, transport)
            self._write('\n\n', transport)
            return True
        elif re.match("show clock", cmd):
            ts = datetime.datetime.now()
            self._write('{}{} UTC {}{}{}\n\n'.format(
                ts.strftime(r'%H:%M:%S'),
                ts.strftime(r'.%f')[:4],
                ts.strftime(r'%a %b '),
                ts.strftime(r'%d').lstrip('0'),
                ts.strftime(r' %Y')), transport)
            return True


    def general_config(self, transport, cmd):
        if 'path bootflash:' in cmd:
            return True
        elif 'platform crft' in cmd:
            return True

    def ctc_enable(self, transport, cmd):
        if cmd == 'dir':
            if self.files_on_flash:
                lines = ['Directory of flash:/', '']
                lines += ['319519  drwx            28672  Jun 11 2021 06:11:45 +00:00 ' + f for f in self.files_on_flash]
                self._write('\n'.join(lines), transport)
                self._write('\n\n', transport)
                return True
            else:
                return False
        elif re.match(r'mkdir flash:/ctc.*', cmd):
            return True
        elif re.match(r'delete /force /recursive ctc.*', cmd):
            m = re.match(r'delete /force /recursive (ctc.*.tar.gz)', cmd)
            filename = m.group(1)
            if filename in self.files_on_flash:
                self.files_on_flash.remove(filename)
            return True
        elif re.match(r'copy ctc_.*', cmd):
            self.set_state(self.transport_handles[transport], 'ctc_copy_address')
            return True

    def ctc_shell_flash(self, transport, cmd):
        if re.match(r'mv flash:/\* ctc.*', cmd):
            return True
        elif re.match(r'tar cfz ctc_.*', cmd):
            m = re.match(r'tar cfz (ctc_.*.tar.gz) .*', cmd)
            filename = m.group(1)
            self.files_on_flash.append(filename)
            return True
        elif re.match(r'rm -rf ctc_.*', cmd):
            return True

    def general_rommon(self, transport, cmd):
        self.rommon_prompt_count += 1
        self.mock_data['general_rommon']['prompt'] = 'rommon{}>'.format(self.rommon_prompt_count)

    def ha_asr1k_enable_reload_to_rommon(self, transport, cmd):
        if cmd == "reload":
            if len(self.transport_ports) > 1:
                self.state_change_switchover(transport, 'ha_asr1k_boot_to_rommon', 'ha_asr1k_boot_to_rommon_stdby')
                other_transport = [t for t in self.transport_handles if t != transport][0]
                prompt = self.transport_ports[self.transport_handles[other_transport]]['prompt']
                self._write('\n'.format(prompt), other_transport)
            return True



class MockDeviceTcpWrapperIOSXE(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='iosxe', **kwargs)

        if 'port' in kwargs:
            kwargs.pop('port')

        if 'stack' in kwargs and kwargs['stack']:
            kwargs.pop('stack')
            self.mockdevice = MockDeviceStackIOSXE(*args, **kwargs)
        elif 'quad' in kwargs and kwargs['quad']:
            kwargs.pop('quad')
            self.mockdevice = MockDeviceQuadIOSXE(*args, **kwargs)
        else:
            self.mockdevice = MockDeviceIOSXE(*args, **kwargs)

class MockDeviceStackIOSXE(MockDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="iosxe", **kwargs)

    def stack_enable(self, transport, cmd):
        port = self.transport_handles[transport]

        if cmd == 'show switch':
            self.update_show_switch(transport)
        if cmd == "redundancy reload shelf":
            ports = [p for p in self.transport_ports.keys() \
                if p != self.transport_handles[transport]]
            if len(ports):
                for port in ports:
                    self.set_state(port, 'stack_rommon')

    def update_show_switch(self, transport):
        port = self.transport_handles[transport]
        switch_no = self.transport_ports[port]['switch_no']
        data  = 'Switch/Stack Mac Address : 5897.bd36.b380 - Local Mac Address\n'\
                'Mac persistency wait time: Indefinite\n'\
                '                                             H/W   Current\n'\
                'Switch#   Role    Mac Address     Priority Version  State\n'\
                '-------------------------------------------------------------------\n'

        for i in self.transport_ports.values():
            switch_line = '{star}{num}       {role}   5897.bd36.b380     3      V01     {state}  \n'
            if i['switch_no'] == switch_no:
                star = '*'
            else:
                star = ' '
            switch_line = switch_line.format(star=star, num=i['switch_no'], role=i['role'], state=i['switch_state'])
            data += switch_line
        self.mock_data['stack_enable']['commands']['show switch'] = data


class MockDeviceQuadIOSXE(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="iosxe", **kwargs)

    def quad_enable(self, transport, cmd):
        port = self.transport_handles[transport]
        ports = [p for p in self.transport_ports.keys() if p != port]

        if cmd == "redundancy force-switchover":
            for idx, port in enumerate(ports):
                if idx == 0:
                    # active ics -> standby
                    self.set_state(port, 'quad_stby_switchover')
                elif idx == 1:
                    # standby -> active
                    self.set_state(port, 'quad_enable')
                else:
                    # standby ics -> active ics
                    self.set_state(port, 'quad_ics_login')

        if cmd == "reload":
            for idx, port in enumerate(ports):
                if idx == 1:
                    # standby
                    self.set_state(port, 'quad_stby_reload')
                else:
                    # standby ics / active ics
                    self.set_state(port, 'quad_ics_reload')


def main(args=None):

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
