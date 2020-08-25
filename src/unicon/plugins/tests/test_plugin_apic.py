"""
Unittests for apic plugin

Uses the mock_device.py script to test the plugin.

"""

__author__ = "karmoham"


import unittest
from unittest.mock import patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure

from unicon.mock.mock_device import MockDeviceSSHWrapper


class TestAciApicPlugin(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os apic --state apic_connect'],
                            os='apic',
                            username='cisco',
                            tacacs_password='cisco')
        c.connect()

    def test_login_connect_credentials(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os apic --state apic_connect'],
                            os='apic',
                            credentials={'default':{
                                'username': 'admin',
                                'password': 'cisco123'}})
        c.connect()

    def test_connect_escape_codes_learn_hostname(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os apic --state apic_hostname_with_escape_codes'],
                            os='apic',
                            username='cisco',
                            tacacs_password='cisco',
                            learn_hostname=True)
        c.connect()

    def test_reload(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os apic --state apic_connect'],
                            os='apic',
                            username='admin',
                            tacacs_password='cisco123')
        c.connect()
        c.settings.POST_RELOAD_WAIT = 1
        c.reload()

    def test_reload_credentails(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os apic --state apic_connect'],
                            os='apic',
                            credentials={'default':{
                                'username': 'admin',
                                'password': 'cisco123'}})
        c.connect()
        c.settings.POST_RELOAD_WAIT = 1
        c.reload()

    def test_config_prompt(self):
        c = Connection(hostname='APC',
                       start=['mock_device_cli --os aci --state apic_connect'],
                       os='apic',
                       credentials={'default':{
                           'username': 'admin',
                           'password': 'cisco123'}})
        c.connect()
        c.configure('tenant test')

    def test_execute_error_pattern(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os apic --state apic_connect'],
                            os='apic',
                            username='cisco',
                            tacacs_password='cisco')
        c.connect()
        for cmd in ['invalid command']:
            with self.assertRaises(SubCommandFailure) as err:
                r = c.execute(cmd)

@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestAciSSH(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.apic_md_ssh = MockDeviceSSHWrapper(hostname='APC', device_os='apic', port=0, state='apic_exec',
                                               credentials={'cisco': 'cisco'})
        cls.apic_md_ssh.start()

        cls.testbed = """
          devices:
              APC:
                os: apic
                type: controller
                credentials:
                    default:
                        username: cisco
                        password: cisco
                    enable:
                        password: cisco123
                connections:
                  defaults:
                    class: unicon.Unicon
                  a:
                    protocol: ssh
                    ip: 127.0.0.1
                    port: {apic_ssh}
        """.format(
                   apic_ssh=cls.apic_md_ssh.ports[0],
                   )
        cls.tb = loader.load(cls.testbed)

    @classmethod
    def tearDownClass(cls):
        cls.apic_md_ssh.stop()

    def test_apic_ssh(self):
        a = self.tb.devices.APC
        a.connect()
        a.disconnect()
        a.connect()
        self.assertEqual(a.connected, True)


if __name__ == "__main__":
    unittest.main()
