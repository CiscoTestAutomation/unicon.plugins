"""
Unittests for NFVIS plugin

Uses the mock_device.py script to test NFVIS plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re
import unittest

from pyats.topology import loader

from unicon import Connection
from unicon.core.errors import SubCommandFailure

class TestConfdNfvisPluginConnect(unittest.TestCase):

    def test_connect_via(self):
        testbed = """
        devices:
          nfvis:
            os: confd
            type: router
            platform: nfvis
            passwords:
                tacacs: "cisco123"
                enable: "cisco123"
                line: "cisco123"
            tacacs:
                username: admin
            connections:
              defaults:
                class: unicon.Unicon
                via: cli
              cli:
                command: mock_device_cli --os confd --state nfvis_login
        """

        tb = loader.load(testbed)
        c = tb.devices.nfvis
        c.connect(via='cli', learn_hostname=True)
        self.assertEqual(c.connected, True)

    def test_connect_nfvis_hostname(self):
        c = Connection(hostname='vbo',
                        start=['mock_device_cli --os confd --state nfvis_login --hostname nfvis'],
                        os='confd',
                        platform='nfvis',
                        username='admin',
                        line_password='cisco123',
                        tacacs_password='cisco123',
                        enable_password ='cisco123')
        c.connect()



class TestConfdNfvisPluginExecute(unittest.TestCase):

    def test_connect(self):
        c = Connection(hostname='vbo',
                        start=['mock_device_cli --os confd --state nfvis_login --hostname vbo'],
                        os='confd',
                        platform='nfvis',
                        username='admin',
                        line_password='cisco123',
                        tacacs_password='cisco123',
                        enable_password ='cisco123')
        c.connect()
        return c

    def test_execute_show_version(self):
        c = self.test_connect()
        r = c.execute('show version')
        self.assertEqual(r, "\r\n".join("""\
version name "Enterprise NFV Infrastructure Software"
version version 3.5.1-FC4
version build-date "Friday, March 31, 2017 [00:12:22 PDT]"
""".splitlines())
        )

    def test_execute_configure(self):
        c = self.test_connect()
        r = c.execute(['config term', 'commit', 'end'])
        self.assertEqual(r, {'commit': '', 'end': '', 'config term': ''})


class TestConfdNfvisPluginConfigure(unittest.TestCase):

    def test_connect(self):
        c = Connection(hostname='vbo',
                        start=['mock_device_cli --os confd --state nfvis_login --hostname vbo'],
                        os='confd',
                        platform='nfvis',
                        username='admin',
                        line_password='cisco123',
                        tacacs_password='cisco123',
                        enable_password ='cisco123')
        c.connect()
        return c

    def test_configure(self):
        c = self.test_connect()
        r = c.configure("no vm_lifecycle images")
        self.assertEqual(r, {'no vm_lifecycle images': '', 'commit': ''})

    def test_configure_error(self):
        c = self.test_connect()
        c.spawn.timeout = 60
        with self.assertRaisesRegex(SubCommandFailure, "sub_command failure, patterns matched in the output"):
            r = c.configure("no bridges bridge mgmt-br", timeout=60)

    def test_configure_should_not_error(self):
        c = self.test_connect()
        c.spawn.timeout = 60
        r = c.configure("no bridges bridge mgmt-br", error_pattern=[], timeout=60)
        self.assertEqual(r['commit'], "Aborted: illegal reference 'networks network mgmt-net bridge'")
        self.assertEqual(c.state_machine.current_cli_mode, 'exec')


if __name__ == "__main__":
    unittest.main()


