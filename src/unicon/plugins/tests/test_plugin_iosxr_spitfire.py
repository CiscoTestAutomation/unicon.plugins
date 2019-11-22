"""
Unittests for IOSXR/SPITFIRE plugin

Uses the mock_device.py script to test IOSXR plugin.

"""

__author__ = "Sritej K V R <skanakad@cisco.com>"

import os
import yaml
import unittest
from unittest.mock import patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.plugins.tests.mock.mock_device_iosxr_spitfire import MockDeviceTcpWrapperSpitfire
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path
import unicon.plugins

patch.TEST_PREFIX = ('test', 'setUp', 'tearDown')


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrSpitfirePluginDevice(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.md = MockDeviceTcpWrapperSpitfire(port=0, state='spitfire_login')
        self.md.start()

        self.testbed = """
        devices:
          Router:
            os: iosxr
            series: spitfire
            type: router
            tacacs:
                username: cisco
            passwords:
                tacacs: cisco123
                enable: cisco123
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(self.md.ports[0])

    def test_connect(self):
        tb = loader.load(self.testbed)
        self.r = tb.devices.Router
        self.r.connect()
        self.assertEqual(self.r.spawn.match.match_output,'end\r\nRP/0/RP0/CPU0:Router#')
        self.r.disconnect()

    @classmethod
    def tearDownClass(self):
        self.md.stop()
        

@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrSpitfirePlugin(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state spitfire_login'],
                            os='iosxr',
                            series='spitfire',
                            username='cisco',
                            enable_password='cisco123',
                            )

    def test_connect(self):
        self.c.connect()
        self.assertEqual(self.c.spawn.match.match_output,'end\r\nRP/0/RP0/CPU0:Router#')

    def test_execute(self):
        r = self.c.execute('show platform')
        with open(os.path.join(mockdata_path, 'iosxr/spitfire/show_platform.txt'), 'r') as outputfile:
            expected_device_output = outputfile.read().strip()
        device_output = r.replace('\r', '').strip()
        self.maxDiff = None
        self.assertEqual(device_output, expected_device_output)
    
    @classmethod
    def tearDownClass(self):
        self.c.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrSpitfirePluginPrompts(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state spitfire_enable'],
                            os='iosxr',
                            series='spitfire',
                            username='cisco',
                            enable_password='cisco123',
                            )
        cls.c.connect()

    def test_xr_bash_prompt(self):
        self.c.state_machine.go_to('xr_bash',self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,'bash\r\n[ios:/misc/scratch]$')
        self.c.state_machine.go_to('enable',self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,'exit\r\nRP/0/RP0/CPU0:Router#')

    def test_xr_run_prompt(self):
        self.c.state_machine.go_to('xr_run',self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,'run\r\n[node0_RP0_CPU0:~]$')
        self.c.state_machine.go_to('enable',self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,'exit\r\nRP/0/RP0/CPU0:Router#')

    def test_xr_env_prompt(self):
        self.c.state_machine.go_to('xr_env',self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,'xrenv\r\nXR[ios:~]$')
        self.c.state_machine.go_to('enable',self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,'exit\r\nRP/0/RP0/CPU0:Router#')

    def test_xr_config_prompt(self):
        self.c.state_machine.go_to('config',self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,'configure terminal\r\nRP/0/RP0/CPU0:Router(config)#')
        self.c.state_machine.go_to('enable',self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,'end\r\nRP/0/RP0/CPU0:Router#')
    
    @classmethod
    def tearDownClass(self):
        self.c.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrSpitfirePluginSvcs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state spitfire_enable'],
                            os='iosxr',
                            series='spitfire',
                            username='cisco',
                            enable_password='cisco123',
                            )
        cls.c.connect()

    def test_execute(self):
        self.c.execute("bash", allow_state_change=True)
        self.assertEqual(self.c.spawn.match.match_output,'bash\r\n[ios:/misc/scratch]$')
    
    @classmethod
    def tearDownClass(self):
        self.c.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrSpitfireHAConnect(unittest.TestCase):
    
    def setUp(self):
        self.md = MockDeviceTcpWrapperSpitfire(port=0,state='spitfire_login,spitfire_console_standby')
        self.md.start()

        self.testbed = """
        devices:
          Router:
            os: iosxr
            series: spitfire
            type: router
            tacacs:
                username: cisco
            passwords:
                tacacs: cisco123
                enable: cisco123
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

        """.format(self.md.ports[0],self.md.ports[1])
        tb = loader.load(self.testbed)
        self.r = tb.devices.Router
        self.r.connect(prompt_recovery=True)

    def test_connect(self):
        self.assertEqual(self.r.active.spawn.match.match_output,'end\r\nRP/0/RP0/CPU0:Router#')
    
    def test_handle(self):
        self.assertEqual(self.r.a.role,"active",)
        self.assertEqual(self.r.b.role,"standby")

    def test_switchover(self):
        self.r.switchover(sync_standby=False)

    def test_switchover_with_sync(self):
        self.r.switchover(sync_standby=True)

    def tearDown(self):
        self.r.disconnect()
        self.md.stop()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrSpitfirePluginConnectReply(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state spitfire_enable'],
                            os='iosxr',
                            series='spitfire',
                            username='cisco',
                            enable_password='cisco123',
                            connect_reply = Dialog([[r'^(.*?)Password:']])
                            )
        cls.c.connect()

    def test_connection_connectReply(self):
        self.assertIn("^(.*?)Password:", str(self.c.connection_provider.get_connection_dialog()))

    @classmethod
    def tearDownClass(self):
        self.c.disconnect()


@patch.object(unicon.plugins.iosxr.spitfire.settings.SpitfireSettings, 'CONFIG_LOCK_TIMEOUT', 5)
@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrSpitfirePluginConnectConfigLock(unittest.TestCase):

    def test_configlocktimeout(self):
        self.md = MockDeviceTcpWrapperSpitfire(port=0,state='spitfire_login')
        self.md.start()

        self.testbed = """
        devices:
          Router:
            os: iosxr
            series: spitfire
            type: router
            tacacs:
                username: cisco
            passwords:
                tacacs: cisco123
                enable: cisco123
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(self.md.ports[0])
        tb = loader.load(self.testbed)
        self.r = tb.devices.Router

        try:
            self.r.connect(prompt_recovery=True)
        except:
            connect_fail =True

        self.assertTrue(connect_fail, "Connection failed ")

    def test_configindefinitelock(self):
        self.md = MockDeviceTcpWrapperSpitfire(port=0,state='spitfire_enable_config_lock')
        self.md.start()

        self.testbed = """
        devices:
          Router:
            os: iosxr
            series: spitfire
            type: router
            tacacs:
                username: cisco
            passwords:
                tacacs: cisco123
                enable: cisco123
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(self.md.ports[0])
        tb = loader.load(self.testbed)
        self.r = tb.devices.Router
    
        try:
            self.r.connect(prompt_recovery=True)
        except:
            connect_fail =True

        self.assertTrue(connect_fail, "Connection failed ")

    def test_configztplock(self):
        self.md = MockDeviceTcpWrapperSpitfire(port=0,state='spitfire_enable_ztp_lock')
        self.md.start()

        self.testbed = """
        devices:
          Router:
            os: iosxr
            series: spitfire
            type: router
            tacacs:
                username: cisco
            passwords:
                tacacs: cisco123
                enable: cisco123
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(self.md.ports[0])
        tb = loader.load(self.testbed)
        self.r = tb.devices.Router
    
        try:
            self.r.connect(prompt_recovery=True)
        except:
            connect_fail =True

        self.assertTrue(connect_fail, "Connection failed ")

    def tearDown(self):
        self.r.disconnect()
        self.md.stop()


if __name__ == "__main__":
    unittest.main()

