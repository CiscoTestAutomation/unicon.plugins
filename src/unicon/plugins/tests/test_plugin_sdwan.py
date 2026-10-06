"""
Unittests for SDWAN plugin

Uses the mock_device_cli script to test.

"""

import re
import unittest

from unicon.core.errors import SubCommandFailure
from unicon import Connection


class TestSDWANPlugin(unittest.TestCase):

    def test_os_viptela(self):
        c = Connection(hostname='vedge',
                            start=['mock_device_cli --os sdwan --state sdwan_exec'],
                            os='viptela',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.execute('')
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'vedge#')

    def test_connect_cisco_exec(self):
        c = Connection(hostname='vedge',
                            start=['mock_device_cli --os sdwan --state sdwan_exec'],
                            os='sdwan',
                            platform='viptela',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.execute('')
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'vedge#')

    def test_connect_and_configure_with_learned_vsmart_hostname(self):
        c = Connection(hostname='vsmart',
                       start=['mock_device_cli --os sdwan --state vsmart_exec'],
                       os='sdwan',
                       platform='viptela',
                       credentials={
                           'default': {
                               'username': 'admin',
                               'password': 'admin',
                           },
                       },
                       settings={
                           'GRACEFUL_DISCONNECT_WAIT_SEC': 0,
                           'POST_DISCONNECT_WAIT_SEC': 0,
                       },
                       learn_hostname=True)

        try:
            c.connect()
            self.assertEqual(c.hostname, 'vm9')
            c.configure('policy')
            self.assertEqual(c.state_machine.current_state, 'cisco_exec')
        finally:
            if c.connected:
                c.disconnect()

    def test_connect_reboot(self):
        c = Connection(hostname='vedge',
                            start=['mock_device_cli --os sdwan --state sdwan_exec'],
                            os='sdwan',
                            platform='viptela',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.settings.RELOAD_WAIT=3
        c.reload()
        c.execute('')
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'vedge#')

    def test_connect_reboot_console(self):
        c = Connection(hostname='vedge',
                            start=['mock_device_cli --os sdwan --state sdwan_console'],
                            os='sdwan',
                            platform='viptela',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.reload()
        c.execute('')
        self.assertEqual(c.spawn.match.match_output.split()[-1], 'vedge#')

    def test_vshell(self):
        c = Connection(hostname='vedge',
                            start=['mock_device_cli --os sdwan --state sdwan_exec'],
                            os='sdwan',
                            platform='viptela',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.execute('vshell')
        c.execute('cd /tmp')
        c.execute('ls -l')
        c.execute('cd')
        c.execute('exit')

    def test_hostname(self):
        c = Connection(hostname='CPE101',
                            start=['mock_device_cli --os sdwan --state sdwan_exec'],
                            os='sdwan',
                            platform='viptela',
                            username='admin',
                            tacacs_password='admin')
        c.connect()
        c.execute('new_hostname')
        c.execute('exec')


if __name__ == "__main__":
    unittest.main()
