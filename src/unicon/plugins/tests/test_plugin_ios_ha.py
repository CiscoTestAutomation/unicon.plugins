
from time import sleep

import unittest
from unittest.mock import Mock, patch

import unicon
from unicon import Connection
from pyats.topology import loader

from unicon.plugins.tests.mock.mock_device_ios import MockDeviceTcpWrapperIOS


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosPluginHAConnect(unittest.TestCase):

    def setUp(self):
        self.md = MockDeviceTcpWrapperIOS(port=0, state='login,exec_standby')
        self.md.start()

        self.testbed = """
        devices:
          Router:
            os: ios
            type: router
            tacacs:
                username: cisco
            passwords:
                tacacs: cisco
                enable: cisco
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
              b:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(self.md.ports[0], self.md.ports[1])

    def tearDown(self):
        self.md.stop()

    def test_connect(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.connect()
        r.disconnect()

    def test_connect_init_commands(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.connect(init_commands=[])
        r.disconnect()

    def test_switchover(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.connect(init_commands=[])
        r.switchover()
        r.disconnect()

    def test_connect_mit(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.connect(mit=True)
        self.assertEqual(r.a.spawn.match.match_output, '\r\nRouter>')
        self.assertEqual(r.b.spawn.match.match_output, '\r\nStandby locked\r\nRouter-stby#')
        with self.assertRaisesRegex(unicon.core.errors.ConnectionError, 'handles are not yet designated'):
            assert r.active is not None
        with self.assertRaisesRegex(unicon.core.errors.ConnectionError, 'handles are not yet designated'):
            assert r.standby is not None



if __name__ == "__main__":
    unittest.main()
