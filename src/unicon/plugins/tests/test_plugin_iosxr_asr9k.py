"""
Unittests for IOSXR/ASR9K plugin

Uses the mock_device.py script to test IOSXR plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import yaml
import unittest

import unicon
from unicon import Connection
from unicon.eal.dialogs import Statement, Dialog
from unicon.mock.mock_device import mockdata_path
from unicon.core.errors import SubCommandFailure

with open(os.path.join(mockdata_path, 'iosxr/iosxr_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestIosXrPluginConnect(unittest.TestCase):

    def test_login_connect_ssh(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state connect_ssh'],
                            os='iosxr',
                            platform='asr9k',
                            username='cisco',
                            line_password='admin',
                            enable_password='admin',
                            )
        c.connect()
        self.assertEqual(c.spawn.match.match_output,'end\r\nRP/0/RP0/CPU0:Router#')


class TestIosXrPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state connect_ssh'],
                            os='iosxr',
                            platform='asr9k',
                            username='cisco',
                            enable_password='admin',
                            line_password='admin',
                            init_exec_commands=[],
                            init_config_commands=[],
                            )
        cls.c.connect()

    def test_execute(self):
        r = self.c.execute('show platform')
        self.assertEqual(r.replace('\r', ''), mock_data['enable']['commands']['show platform'].strip())

    def test_admin(self):
        r = self.c.admin_execute('show platform')
        self.assertEqual(r.replace('\r', ''), mock_data['admin']['commands']['show platform'].strip())

    def test_admin_enable_asr9k(self):
        c = Connection(hostname='PE1',
                            start=['mock_device_cli --os iosxr --state asr9k_enable'],
                            os='iosxr',
                            platform='asr9k',
                            username='cisco',
                            line_password='admin',
                            tacacs_password='admin',
                            )
        c.connect()
        c.state_machine.go_to('admin', c.spawn)
        self.assertEqual(c.spawn.match.match_output,'admin\r\nRP/0/RSP1/CPU0:PE1(admin)#')

    def test_get_rp_state_asr9k(self):
        c = Connection(hostname='PE1',
                            start=['mock_device_cli --os iosxr --state asr9k_enable',
                                   'mock_device_cli --os iosxr --state asr9k_enable'],
                            os='iosxr',
                            platform='asr9k',
                            username='cisco',
                            line_password='admin',
                            tacacs_password='admin',
                            )
        c.connect()
        state = c.get_rp_state()
        self.assertEqual(state, 'ACTIVE')


class TestIosXRAsr9kReload(unittest.TestCase):

    def test_reload_with_error_pattern(self):
        d = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxr --state asr9k_enable --hostname PE1'],
            os='iosxr',
            platform='asr9k'
        )
        install_add_one_shot_dialog = Dialog([
                Statement(pattern=r"FAILED:.* ",
                          action=None,
                          loop_continue=False,
                          continue_timer=False),
         ])
        error_pattern=[r"FAILED:.* ",]

        try:
            d.connect()
            d.settings.STACK_POST_RELOAD_SLEEP = 0
            with self.assertRaises(SubCommandFailure):
                d.reload('active_install_add',
                          reply=install_add_one_shot_dialog,
                          error_pattern = error_pattern)
            self.assertEqual(d.reload.error_pattern, error_pattern)
        finally:
             d.disconnect()

if __name__ == "__main__":
    unittest.main()

