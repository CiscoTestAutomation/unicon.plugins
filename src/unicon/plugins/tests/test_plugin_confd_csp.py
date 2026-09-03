"""
Unittests for ConfD/CSP plugin

Uses the mock_device.py script to test plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re
import unittest

import unicon

from pyats.topology import loader

from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unittest.mock import patch

@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestConfdCspPlugin(unittest.TestCase):

    def test_connect_via(self):
        testbed = """
        devices:
          csp-2100:
            os: confd
            type: router
            platform: csp
            passwords:
                tacacs: "admin"
                enable: "admin"
            tacacs:
                username: admin
            connections:
              defaults:
                class: unicon.Unicon
                via: cli
              cli:
                command: mock_device_cli --os confd --state csp_login
        """

        tb = loader.load(testbed)
        c = tb.devices['csp-2100']
        c.connect(via='cli')
        self.assertEqual(c.connected, True)

    def test_connect_via_learn_hostname(self):
        testbed = """
        devices:
          csp:
            os: confd
            type: router
            platform: csp
            alias: uut
            passwords:
                tacacs: "admin"
                enable: "admin"
            tacacs:
                username: admin
            connections:
              defaults:
                class: unicon.Unicon
                via: cli
              cli:
                command: mock_device_cli --os confd --state csp_login
        """

        tb = loader.load(testbed)
        c = tb.devices['uut']
        c.connect(via='cli', learn_hostname=True)
        self.assertEqual(c.connected, True)

    def test_connect(self):
        c = Connection(hostname='csp-2100',
                        start=['mock_device_cli --os confd --state csp_login'],
                        os='confd',
                        platform='csp',
                        username='admin',
                        tacacs_password='admin',
                        enable_password ='admin')
        c.connect()
        return c

    def test_execute_show_version(self):
        c = self.test_connect()
        r = c.execute('show version')

    def test_reload_via_console(self):
        c1 = Connection(hostname='ucs-c220-m3',
                            start=['mock_device_cli --os confd --state cimc_ssh_password'],
                            os='cimc',
                            username='admin',
                            line_password='cisco',
                            tacacs_password='cisco',
                            enable_password ='cisco')
        c2 = Connection(hostname='csp-2100',
                        start=['connect host'],
                        os='confd',
                        platform='csp',
                        username='admin',
                        tacacs_password='cisco',
                        enable_password ='cisco',
                        proxy_connections=[c1],
                        init_config_commands=[])
        c2.connect()
        c2.settings.RELOAD_WAIT = 1
        r = c2.reload()
        self.assertEqual(len(r), 60405)

    def test_reload_via_non_console(self):
        c = Connection(hostname='csp-2100',
                        start=['mock_device_cli --os confd --state csp_enable'],
                        os='confd',
                        platform='csp',
                        username='admin',
                        tacacs_password='cisco',
                        enable_password ='cisco',
                        init_config_commands=[])
        c.connect()
        c.settings.RELOAD_WAIT = 1
        r = c.reload()
        from unicon.utils import Utils
        c.execute('show version')
        output = Utils().remove_ansi_escape_codes(c.spawn.match.match_output.splitlines()[-1])
        self.assertEqual(output, 'csp-2100#')


if __name__ == "__main__":
    unittest.main()


