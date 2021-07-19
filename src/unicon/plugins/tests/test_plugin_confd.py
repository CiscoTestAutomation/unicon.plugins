"""
Unittests for NSO plugin

Uses the unicon.plugins.tests.mock.mock_device_confd script to test the connect, execute and configure services.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import os
import re
import yaml
import unittest

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'confd/confd_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())



class TestConfdPluginConnect(unittest.TestCase):

    def test_connect_cisco_exec(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'user@ncs#')

    def test_connect_juniper_exec(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'user@ncs>')

    def test_connect_cisco_config(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_config'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'user@ncs#')

    def test_connect_juniper_config(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_config'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'user@ncs>')

    def test_connect_hostname_with_dash_and_dot(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_exec2'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'user.name@ncs-hostname.domain#')



class TestConfdPluginExecute(unittest.TestCase):

    def test_cisco_execute_show_services(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.execute('show services')
        self.assertEqual(r, """\
services sw-init-l3vpn foo
 modified devices [ CE1 PE1 ]
 directly-modified devices [ CE1 PE1 ]
 device-list [ CE1 PE1 ]""".replace('\n', '\r\n'))

    def test_cisco_execute_show_services_cisco_style(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.execute('show services', style='cisco')
        self.assertEqual(r, """\
services sw-init-l3vpn foo
 modified devices [ CE1 PE1 ]
 directly-modified devices [ CE1 PE1 ]
 device-list [ CE1 PE1 ]""".replace('\n', '\r\n'))

    def test_cisco_execute_show_services_juniper_style(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.execute('show services', style='juniper')
        self.assertEqual(r, """\
                                                                                     USED BY                                                                      
                             LSA                              LSA                    CUSTOMER                          CONFIG                                     
NAME  DEVICES      SERVICES  SERVICES  DEVICES      SERVICES  SERVICES  DEVICE LIST  SERVICE   ID  STATUS  NAME  TIME  DATA    ERROR  WHEN  TYPE  LEVEL  MESSAGE  
------------------------------------------------------------------------------------------------------------------------------------------------------------------
foo   [ CE1 PE1 ]  -         -         [ CE1 PE1 ]  -         -         [ CE1 PE1 ]  -                                                                            

[ok][2017-05-11 18:54:41]""".replace('\n', '\r\n'))

    def test_cisco_execute_configure(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.execute('configure')
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """\
configure
Entering configuration mode terminal
user@ncs(config)# """)

    def test_juniper_execute_show_services(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.execute('show services')
        self.assertEqual(r, """\
                                                                                     USED BY                                                                      
                             LSA                              LSA                    CUSTOMER                          CONFIG                                     
NAME  DEVICES      SERVICES  SERVICES  DEVICES      SERVICES  SERVICES  DEVICE LIST  SERVICE   ID  STATUS  NAME  TIME  DATA    ERROR  WHEN  TYPE  LEVEL  MESSAGE  
------------------------------------------------------------------------------------------------------------------------------------------------------------------
foo   [ CE1 PE1 ]  -         -         [ CE1 PE1 ]  -         -         [ CE1 PE1 ]  -                                                                            

[ok][2017-05-11 18:54:41]""".replace('\n', '\r\n'))

    def test_juniper_execute_switch_cli_configure(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.command('switch cli')
        c.execute('configure')
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """\
configure
Entering configuration mode private
[ok][1970-01-01 00:00:00]  

[edit]
user@ncs% """)

    def test_juniper_execute_configure(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.execute('configure')
        self.assertEqual(r, """Entering configuration mode private\r
[ok][1970-01-01 00:00:00]  \r\n\n[edit]""")

    def test_cisco_execute_command_list(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.execute(['screen-length 0','screen-width 0'], style='cisco')
        self.assertEqual(r, {'screen-width 0': '', 'screen-length 0': ''})

    def test_execute_with_style_option(self):
        """ Test execute command with start style cisco and execute style juniper
        Expected state after execution: cisco style
        """
        c = Connection(hostname='ncs',
                        start=['mock_device_cli --os confd --state cisco_exec'],
                        os='confd',
                        username='admin',
                        tacacs_password='admin')
        c.connect()
        r = c.execute('show services', style='juniper')
        c.state_machine.detect_state(c.spawn)
        self.assertEqual(c.state_machine.current_cli_style, 'cisco')

    def test_execute_switch_cli_with_other_commands(self):
        """ 'switch cli' together with other commands is supported
        """
        c = Connection(hostname='ncs',
                        start=['mock_device_cli --os confd --state juniper_exec'],
                        os='confd',
                        username='admin',
                        tacacs_password='admin')
        c.connect()
        r = c.execute(['switch cli', 'show services'])
        self.assertEqual(r['show services'], """\
services sw-init-l3vpn foo
 modified devices [ CE1 PE1 ]
 directly-modified devices [ CE1 PE1 ]
 device-list [ CE1 PE1 ]""".replace('\n', '\r\n'))

    def test_trim_buffer_with_execute(self):
        c = Connection(hostname='ncs',
                       start=['mock_device_cli --os confd --state cisco_exec'],
                       os='confd',
                       username='admin',
                       tacacs_password='admin')
        c.connect()
        c.settings.IGNORE_CHATTY_TERM_OUTPUT = True
        c.sendline('rest commit')
        r = c.execute('show services')
        self.assertEqual(r.replace('\r',''),
            mock_data['cisco_exec']['commands']['show services']['response'].rstrip())

    def test_execute_with_yes_no_prompt(self):
        c = Connection(hostname='ncs',
                        start=['mock_device_cli --os confd --state cisco_exec'],
                        os='confd',
                        username='admin',
                        tacacs_password='admin')
        c.connect()
        c.execute('request software reset', timeout=15)
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'user@ncs#')



class TestConfdPluginConfigure(unittest.TestCase):

    maxDiff = None

    def test_cisco_config(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        cmd = 'services sw-init-l3vpn foo endpoint PE2 pe-interface 0/0/0/1 ce CE1 ce-interface 0/1 ce-address 1.1.1.1 pe-address 1.1.1.2'
        r = c.configure(cmd)
        self.assertEqual(r['commit'], 'Commit complete.')

    def test_cisco_config_error(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        try:
            cmd = 'services sw-init-l3vpn foo endpoint PE1 pe-interface 0/0/0/1 ce CE1 ce-interface 0/1 ce-address 1.1.1.1 pe-address 1.1.1.2'
            c.configure(cmd)
        except SubCommandFailure as e:
            self.assertEqual(str(e), "('sub_command failure, patterns matched in the output:', ['Aborted'], 'service result', 'commit\\r\\nAborted: Network Element Driver: device CE1: out of sync\\r\\nadmin@ncs(config-endpoint-PE1)# *** ALARM out-of-sync: Device CE1 is out of sync\\r\\nadmin@ncs(config-endpoint-PE1)# ')")
        else:
            raise AssertionError('Commit error not detected')

    def test_juniper_config(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        cmd = 'services sw-init-l3vpn foo endpoint PE2 pe-interface 0/0/0/1 ce CE1 ce-interface 0/1 ce-address 1.1.1.1 pe-address 1.1.1.2'
        r = c.configure(cmd)
        self.assertEqual(r['commit'], 'Commit complete.')
        self.assertEqual(r[cmd].replace(' \x08', ''), '')

    def test_juniper_execute_config(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_login'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        cmd = 'services sw-init-l3vpn foo endpoint PE2 pe-interface 0/0/0/1 ce CE1 ce-interface 0/1 ce-address 1.1.1.1 pe-address 1.1.1.2'
        r = c.execute(['configure', cmd, 'commit'])
        self.assertEqual(r['commit'], 'Commit complete.\r\n\n[edit]')

    def test_cisco_configure_command_list(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.configure(['services abc','commit'], style='cisco')
        self.assertEqual(r, {'commit': 'Commit complete.', 'services abc': ''})


class TestConfdPluginCliStyle(unittest.TestCase):


    def test_cisco_to_juniper_exec_clistyle(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.cli_style(style='j')
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """\
switch cli
[ok][1970-01-01 00:00:00]
user@ncs> """)

    def test_juniper_to_cisco_exec_clistyle(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.cli_style(style='c')
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """\
switch cli
user@ncs# """)

    def test_cisco_to_juniper_config_clistyle(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_config'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.execute('configure')
        c.cli_style(style='j')
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """\
switch cli
[ok][1970-01-01 00:00:00]

[edit]
user@ncs% """)

    def test_juniper_to_cisco_config_clistyle(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_config'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.execute('configure')
        c.cli_style(style='c')
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """\
switch cli
user@ncs(config)# """)



class TestConfdPluginCommand(unittest.TestCase):

    def test_command_cisco_exec(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.command('screen-length 0')
        self.assertEqual(r, "screen-length 0\r\nuser@ncs# ")

    def test_command_juniper_exec(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.command('set screen length 0')
        assert r == "set screen length 0\r\nuser@ncs> "

    def test_command_cisco_config(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state cisco_exec'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.command('config')
        self.assertEqual("\n".join(r.splitlines()), """config
Entering configuration mode terminal
user@ncs(config)# """)

    def test_command_juniper_config(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_config'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        r = c.command('configure')
        self.assertEqual("\n".join(r.splitlines()), """configure
Entering configuration mode private
[ok][1970-01-01 00:00:00]  

[edit]
user@ncs% """)


class TestConfdPluginErrorPattern(unittest.TestCase):

    def test_detect_error_pattern(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_exec_syntax_error'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        with self.assertRaisesRegex(SubCommandFailure, 'sub_command failure, patterns matched in the output'):
            c.execute('show command error', error_pattern=['---\^'])


    def test_ignore_error_pattern(self):
        c = Connection(hostname='ncs',
                            start=['mock_device_cli --os confd --state juniper_exec_syntax_error'],
                            os='confd',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        self.assertEqual(c.execute('show command error', error_pattern=[]),
            '-----------------------------^\r\nsyntax error: unknown argument')


    def test_error_pattern_settings(self):
        testbed = """
        devices:
          ncs:
            os: confd
            type: nso
            connections:
              a:
                ip: localhost
              cli:
                class: unicon.Unicon
                command: mock_device_cli --os confd --state juniper_exec_syntax_error
        """

        tb = loader.load(testbed)
        ncs = tb.devices.ncs

        ncs.connect(via='cli')
        ncs.settings.ERROR_PATTERN=['---\^']

        with self.assertRaisesRegex(SubCommandFailure, 'sub_command failure, patterns matched in the output'):
            ncs.execute('show command error')



if __name__ == "__main__":
    unittest.main()
