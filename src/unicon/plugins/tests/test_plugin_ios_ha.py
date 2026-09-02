from copy import copy
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
        self.md = MockDeviceTcpWrapperIOS(port=0,
            state='login,exec_standby')
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

        self.testbed_custom_subconnection = """
        devices:
          Router:
            os: ios
            type: router
            credentials:
                default:
                    username: cisco
                    password: cisco
            connections:
              defaults:
                class: unicon.Unicon
                connections: [one, two]
              one:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
              two:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(self.md.ports[0], self.md.ports[1])

    def tearDown(self):
        self.md.stop()

    def test_connect(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.instantiate()
        r.connect()
        self.assertEqual(r.get_mode(), 'sso')
        self.assertTrue(r.active is r.a)
        self.assertTrue(r.standby is r.b)
        self.assertEqual(r.get_rp_state(), 'ACTIVE')
        self.assertEqual(r.get_rp_state(target='standby'), 'STANDBY HOT')
        self.assertEqual(r.get_rp_state(target='b'), 'STANDBY HOT')
        self.assertEqual(r.standby.execute(''), '')
        self.assertEqual(r.b.execute(''), '')
        self.assertEqual(r.execute(''), '')
        self.assertEqual(r.active.execute(''), '')
        r.disconnect()

    def test_connect_ha_start(self):
        self.md.stop()
        self.md = MockDeviceTcpWrapperIOS(port=0, state='login,exec_standby',
            hostname='my_ha_device')
        self.md.start()
        r = Connection(
            hostname='myhost',
            start=['telnet 127.0.0.1 {}'.format(self.md.ports[0]),
            'telnet 127.0.0.1 {}'.format(self.md.ports[1])],
            credentials=dict(default=dict(username='cisco', password='cisco')),
            learn_hostname=True)
        r.connect()
        self.assertEqual(r.hostname, 'my_ha_device')
        self.assertEqual(r.a.hostname, 'my_ha_device')
        self.assertEqual(r.b.hostname, 'my_ha_device')
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
        self.assertEqual(r.get_mode(), 'sso')
        self.assertTrue(r.active is r.b)
        self.assertTrue(r.standby is r.a)
        self.assertEqual(r.get_rp_state(), 'ACTIVE')
        self.assertEqual(r.get_rp_state(target='standby'), 'STANDBY HOT')
        self.assertEqual(r.get_rp_state(target='a'), 'STANDBY HOT')
        self.assertEqual(r.standby.execute(''), '')
        self.assertEqual(r.a.execute(''), '')
        self.assertEqual(r.execute(''), '')
        self.assertEqual(r.active.execute(''), '')
        r.switchover()
        self.assertEqual(r.get_mode(), 'sso')
        self.assertTrue(r.active is r.a)
        self.assertTrue(r.standby is r.b)
        self.assertEqual(r.get_rp_state(), 'ACTIVE')
        self.assertEqual(r.get_rp_state(target='standby'), 'STANDBY HOT')
        self.assertEqual(r.get_rp_state(target='b'), 'STANDBY HOT')
        self.assertEqual(r.standby.execute(''), '')
        self.assertEqual(r.b.execute(''), '')
        self.assertEqual(r.execute(''), '')
        self.assertEqual(r.active.execute(''), '')
        r.disconnect()

    def test_switchover_custom_vias(self):
        tb = loader.load(self.testbed_custom_subconnection)
        r = tb.devices.Router
        r.connect(init_commands=[])
        r.switchover()
        self.assertEqual(r.get_mode(), 'sso')
        self.assertTrue(r.active is r.two)
        self.assertTrue(r.standby is r.one)
        self.assertEqual(r.get_rp_state(), 'ACTIVE')
        self.assertEqual(r.get_rp_state(target='standby'), 'STANDBY HOT')
        self.assertEqual(r.get_rp_state(target='one'), 'STANDBY HOT')
        self.assertEqual(r.standby.execute(''), '')
        self.assertEqual(r.one.execute(''), '')
        self.assertEqual(r.execute(''), '')
        self.assertEqual(r.active.execute(''), '')
        r.switchover()
        self.assertEqual(r.get_mode(), 'sso')
        self.assertTrue(r.active is r.one)
        self.assertTrue(r.standby is r.two)
        self.assertEqual(r.get_rp_state(), 'ACTIVE')
        self.assertEqual(r.get_rp_state(target='standby'), 'STANDBY HOT')
        self.assertEqual(r.get_rp_state(target='two'), 'STANDBY HOT')
        self.assertEqual(r.standby.execute(''), '')
        self.assertEqual(r.two.execute(''), '')
        self.assertEqual(r.execute(''), '')
        self.assertEqual(r.active.execute(''), '')
        r.disconnect()

    def test_connect_mit(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.connect(mit=True)
        self.assertEqual(r.a.spawn.match.match_output, '\r\nRouter>')
        self.assertEqual(r.b.spawn.match.match_output, '\r\nRouter-stby#')
        with self.assertRaisesRegex(unicon.core.errors.ConnectionError, 'handles are not yet designated'):
            assert r.active is not None
        with self.assertRaisesRegex(unicon.core.errors.ConnectionError, 'handles are not yet designated'):
            assert r.standby is not None


if __name__ == "__main__":
    unittest.main()
