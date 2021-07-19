"""
Unittests for NXOS aci plugin

Uses the mock_device.py script to test the plugin.

"""

__author__ = "karmoham"


import unittest
from unittest.mock import patch

from pyats.topology import loader

import unicon
from unicon import Connection

from unicon.mock.mock_device import MockDeviceSSHWrapper


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestNxosAciPlugin(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='LEAF',
                       start=['mock_device_cli --os nxos --state n9k_connect --hostname LEAF'],
                       os='nxos',
                       platform='aci',
                       model='n9k',
                       username='admin',
                       tacacs_password='cisco123')
        c.connect()
        c.disconnect()

    def test_login_connect_credentials(self):
        c = Connection(hostname='LEAF',
                       start=['mock_device_cli --os nxos --state n9k_login --hostname LEAF'],
                       os='nxos',
                       platform='aci',
                       model='n9k',
                       credentials={'default': {
                           'username': 'admin',
                           'password': 'cisco123'
                       }})
        c.connect()
        c.disconnect()

    def test_reload(self):
        c = Connection(hostname='LEAF',
                       start=['mock_device_cli --os nxos --state n9k_login --hostname LEAF'],
                       os='nxos',
                       platform='aci',
                       tacacs_password='cisco123')
        c.connect()
        c.settings.POST_RELOAD_WAIT = 1
        c.reload()
        c.disconnect()

    def test_attach_console(self):
        c = Connection(hostname='LEAF',
                       start=['mock_device_cli --os nxos --state n9k_login --hostname LEAF'],
                       os='nxos',
                       platform='aci',
                       tacacs_password='cisco123')
        c.connect()
        with c.attach_console() as mod:
            mod.execute('')
        c.disconnect()

    def test_attach(self):
        c = Connection(hostname='LEAF',
                       start=['mock_device_cli --os nxos --state n9k_login --hostname LEAF'],
                       os='nxos',
                       platform='aci',
                       tacacs_password='cisco123')
        c.connect()
        with c.attach(1) as mod:
            mod.execute('')
        c.disconnect()


class TestNxosAciSSH(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.aci_n9k_md_ssh = MockDeviceSSHWrapper(hostname='LEAF', device_os='nxos', port=0, state='n9k_exec',
                                                  credentials={'cisco': 'cisco'})
        cls.aci_n9k_md_ssh.start()

        cls.testbed = """
          devices:
              LEAF:
                os: nxos
                platform: aci
                model: n9k
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
                    ssh_options: -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
        """.format(n9k_ssh=cls.aci_n9k_md_ssh.ports[0])
        cls.tb = loader.load(cls.testbed)

    @classmethod
    def tearDownClass(cls):
        cls.aci_n9k_md_ssh.stop()

    def test_aci_n9k_ssh(self):
        n = self.tb.devices.LEAF
        n.connect()
        n.disconnect()
        n.connect()
        self.assertEqual(n.connected, True)
        n.disconnect()


if __name__ == "__main__":
    unittest.main()
