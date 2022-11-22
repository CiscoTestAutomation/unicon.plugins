"""
Unittests for NXOS/N7K plugin
"""

import unittest

import unicon
from unicon import Connection

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestNxosVDC(unittest.TestCase):

    def test_connect_login(self):
        c = Connection(hostname='admin',
                       start=['mock_device_cli --os nxos --state login'],
                       os='nxos',
                       platform='n7k',
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True,
                       credentials=dict(default=dict(username='cisco', password='cisco'))
                       )
        c.connect()
        c.execute('show version')

    def test_connect_to_non_default_vdc(self):
        c = Connection(hostname='admin',
                       start=['mock_device_cli --os nxos --state vdc_exec'],
                       os='nxos',
                       platform='n7k',
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True)
        c.connect()
        c.switchback()
        c.configure()

    def test_connect_to_non_default_vdc_with_learn_hostname(self):
        c = Connection(hostname='admin',
                       start=['mock_device_cli --os nxos --state vdc_exec'],
                       os='nxos',
                       platform='n7k',
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True,
                       learn_hostname=True)
        c.connect()
        c.switchback()
        c.configure()

    def test_connect_default_vdc_with_more_prompt(self):
        c = Connection(hostname='N7K-B',
                       start=['mock_device_cli --os nxos --state vdc_exec2'],
                       os='nxos',
                       platform='n7k',
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True,
                       learn_hostname=True,
                       mit=True)
        c.connect()
        c.switchback()


if __name__ == "__main__":
    unittest.main()
