"""
Unittests for Junos plugin

Uses the unicon.plugins.tests.mock.mock_device_junos script to test Junos plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import os
import re
import yaml
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'junos/junos_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestJunosPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='junos_vmx2',
                        start=['mock_device_cli --os junos --state exec'],
                        os='junos',
                        username='root',
                        tacacs_password='lab')
        c.connect()
        self.assertIn('set cli screen-width 0', c.spawn.match.match_output)
        self.assertIn('root@junos_vmx2>', c.spawn.match.match_output)
        c.disconnect()

    def test_login_connect_ssh(self):
        c = Connection(hostname='junos_vmx2',
                        start=['mock_device_cli --os junos --state connect_ssh'],
                        os='junos',
                        username='root',
                        tacacs_password='lab')
        c.connect()
        self.assertIn('set cli screen-width 0', c.spawn.match.match_output)
        self.assertIn('root@junos_vmx2>', c.spawn.match.match_output)
        c.disconnect()

    def test_login_connect_connectReply(self):
        c = Connection(hostname='junos_vmx2',
                        start=['mock_device_cli --os junos --state exec'],
                        os='junos',
                        username='root',
                        tacacs_password='lab',
                        connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn('set cli screen-width 0', c.spawn.match.match_output)
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestJunosPluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        c = Connection(hostname='junos_vmx2',
                        start=['mock_device_cli --os junos --state exec'],
                        os='junos',
                        username='root',
                        tacacs_password='lab',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        cmd = 'show interfaces terse | match fxp0'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)
        c.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestJunosPluginConfigure(unittest.TestCase):

    def test_configure_commit(self):
        c = Connection(hostname='junos_vmx2',
                        start=['mock_device_cli --os junos --state exec'],
                        os='junos',
                        username='root',
                        tacacs_password='lab',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        cmd = 'commit'
        expected_response = mock_data['config']['commands'][cmd].strip()
        ret = c.configure(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)
        c.disconnect()

    def test_configure_commit_on_failure(self):
        c = Connection(hostname='junos_dev',
                        start=['mock_device_cli --os junos --state exec3'],
                        os='junos',
                        username='root',
                        tacacs_password='lab',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        with self.assertRaises(SubCommandFailure):
            c.configure('commit')
        c.disconnect()

    def test_configure_commit_on_failure_1(self):
        c = Connection(hostname='junos_dev',
                        start=['mock_device_cli --os junos --state exec4'],
                        os='junos',
                        username='root',
                        tacacs_password='lab',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        with self.assertRaises(SubCommandFailure):
            c.configure('commit')
        c.disconnect()

    def test_configure_commit_cmd(self):
        c = Connection(hostname='junos_vmx2',
                       start=['mock_device_cli --os junos --state exec'],
                       os='junos',
                       mit=True)
        c.connect()
        c.configure.commit_cmd = ""
        c.configure("something")
        self.assertNotIn('commit', c.spawn.match.match_output)
        c.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestJunosPluginBashService(unittest.TestCase):

    def test_bash(self):
        c = Connection(hostname='junos_vmx2',
                       start=['mock_device_cli --os junos --state exec'],
                       os='junos',
                       username='root',
                       tacacs_password='lab')

        with c.bash_console() as console:
            console.execute('ls')
        self.assertIn('cli', c.spawn.match.match_output)
        self.assertIn('root@junos_vmx2>', c.spawn.match.match_output)
        c.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestJunosVsrxPluginBashService(unittest.TestCase):

    def test_bash(self):
        c = Connection(hostname='junos_vsrx',
                       start=['mock_device_cli --os junos --state exec2'],
                       os='junos',
                       platform='vsrx',
                       username='root',
                       tacacs_password='lab')

        with c.bash_console() as console:
            console.execute('ls')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('root@junos_vsrx>', c.spawn.match.match_output)
        c.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestConfigErrorResponse(unittest.TestCase):

    def test_connection(self):
        c = Connection(hostname='junos_dev',
                        start=['mock_device_cli --os junos --state exec5'],
                        os='junos',
                        username='root',
                        tacacs_password='lab',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        with self.assertRaises(Exception):
            c.configure('commit synchronize')
        c.disconnect()


if __name__ == "__main__":
    unittest.main()
