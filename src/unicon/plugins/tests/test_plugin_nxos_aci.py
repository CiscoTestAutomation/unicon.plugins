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
from unicon.core.errors import SubCommandFailure

from unicon.mock.mock_device import MockDeviceSSHWrapper


class TestNxosAciPlugin(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='LEAF',
                            start=['mock_device_cli --os nxos --state n9k_connect'],
                            os='nxos',
                            series='aci',
                            model='n9k',
                            username='admin',
                            tacacs_password='cisco123')
        c.connect()

    def test_login_connect_credentials(self):
        c = Connection(hostname='LEAF',
                            start=['mock_device_cli --os nxos --state n9k_login'],
                            os='nxos',
                            series='aci',
                            model='n9k',
                            credentials={'default':{
                                'username': 'admin',
                                'password': 'cisco123'}})
        c.connect()

    def test_reload(self):
        c = Connection(hostname='LEAF',
                            start=['mock_device_cli --os nxos --state n9k_login'],
                            os='nxos',
                            series='aci',
                            model='n9k',
                            username='admin',
                            tacacs_password='cisco123')
        c.connect()
        c.settings.POST_RELOAD_WAIT = 1
        c.reload()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
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
                series: aci
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
        """.format(
                   n9k_ssh=cls.aci_n9k_md_ssh.ports[0],
                   )
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


if __name__ == "__main__":
    unittest.main()
