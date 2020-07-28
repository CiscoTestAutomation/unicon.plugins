"""
Unittests for aci plugin

Uses the mock_device.py script to test the plugin.

"""

__author__ = "dwapstra"


import unittest
from unittest.mock import patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure

from unicon.mock.mock_device import MockDeviceSSHWrapper


class TestAciApicPlugin(unittest.TestCase):

    # ==================
    # old Implementation
    # ==================
    def test_login_connect_old(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os aci --state apic_connect'],
                            os='aci',
                            series='apic',
                            username='cisco',
                            tacacs_password='cisco')
        c.connect()

    def test_login_connect_credentials_old(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os aci --state apic_connect'],
                            os='aci',
                            series='apic',
                            credentials={'default':{
                                'username': 'admin',
                                'password': 'cisco123'}})
        c.connect()

    def test_connect_escape_codes_learn_hostname_old(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os aci --state apic_hostname_with_escape_codes'],
                            os='aci',
                            series='apic',
                            username='cisco',
                            tacacs_password='cisco',
                            learn_hostname=True)
        c.connect()

    def test_reload_old(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os aci --state apic_connect'],
                            os='aci',
                            series='apic',
                            username='admin',
                            tacacs_password='cisco123')
        c.connect()
        c.settings.POST_RELOAD_WAIT = 1
        c.reload()

    def test_reload_credentails_old(self):
        c = Connection(hostname='APC',
                            start=['mock_device_cli --os aci --state apic_connect'],
                            os='aci',
                            series='apic',
                            credentials={'default':{
                                'username': 'admin',
                                'password': 'cisco123'}})
        c.connect()
        c.settings.POST_RELOAD_WAIT = 1
        c.reload()

    def test_config_prompt(self):
        c = Connection(hostname='APC',
                       start=['mock_device_cli --os aci --state apic_connect'],
                       os='aci',
                       series='apic',
                       credentials={'default':{
                           'username': 'admin',
                           'password': 'cisco123'}})
        c.connect()
        c.configure('tenant test')


class TestAciN9kPlugin(unittest.TestCase):

    # ==================
    # old Implementation
    # ==================
    def test_login_connect_old(self):
        c = Connection(hostname='LEAF',
                            start=['mock_device_cli --os aci --state n9k_login'],
                            os='aci',
                            series='n9k',
                            username='admin',
                            tacacs_password='cisco123')
        c.connect()

    def test_login_connect_credentials_old(self):
        c = Connection(hostname='LEAF',
                            start=['mock_device_cli --os aci --state n9k_login'],
                            os='aci',
                            series='n9k',
                            credentials={'default':{
                                'username': 'admin',
                                'password': 'cisco123'}})
        c.connect()

    def test_reload_old(self):
        c = Connection(hostname='LEAF',
                            start=['mock_device_cli --os aci --state n9k_login'],
                            os='aci',
                            series='n9k',
                            username='admin',
                            tacacs_password='cisco123')
        c.connect()
        c.settings.POST_RELOAD_WAIT = 1
        c.reload()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestAciSSH(unittest.TestCase):

    # ==================
    # old Implementation
    # ==================
    @classmethod
    def setUpClass(cls):
        cls.apic_md_ssh = MockDeviceSSHWrapper(hostname='APC', device_os='aci', port=0, state='apic_exec',
                                               credentials={'cisco': 'cisco'})
        cls.aci_n9k_md_ssh = MockDeviceSSHWrapper(hostname='LEAF', device_os='aci', port=0, state='n9k_exec',
                                               credentials={'cisco': 'cisco'})
        cls.apic_md_ssh.start()
        cls.aci_n9k_md_ssh.start()

        cls.testbed = """
          devices:
              APC:
                os: aci
                series: apic
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
              LEAF:
                os: aci
                series: n9k
                type: switch
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
                    port: {n9k_ssh}
        """.format(
                   apic_ssh=cls.apic_md_ssh.ports[0],
                   n9k_ssh=cls.aci_n9k_md_ssh.ports[0],
                   )
        cls.tb = loader.load(cls.testbed)

    @classmethod
    def tearDownClass(cls):
        cls.apic_md_ssh.stop()
        cls.aci_n9k_md_ssh.stop()

    def test_apic_ssh(self):
        a = self.tb.devices.APC
        a.connect()
        a.disconnect()
        a.connect()
        self.assertEqual(a.connected, True)

    def test_aci_n9k_ssh(self):
        n = self.tb.devices.LEAF
        n.connect()
        n.disconnect()
        n.connect()
        self.assertEqual(n.connected, True)


if __name__ == "__main__":
    unittest.main()
