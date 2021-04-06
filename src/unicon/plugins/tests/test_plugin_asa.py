"""
Unittests for asa plugin

Uses the mock_device.py script to test the plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import os
import yaml
import unittest


import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'asa/asa_mock_data.yaml'), 'rb') as data:
    mock_data = yaml.safe_load(data.read())


class TestAsaPluginConnect(unittest.TestCase):

    def test_connect(self):
        c = Connection(hostname='ASA',
                       start=['mock_device_cli --os asa --state asa_disable'],
                       os='asa',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        v = c.execute('show version')
        self.assertEqual(v.replace('\r',''), mock_data['asa_enable']['commands']['show version'].rstrip())

    def test_connect_from_username_replication(self):
        c = Connection(hostname='ASA',
                       start=['mock_device_cli --os asa --state asa_username_replication'],
                       os='asa',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
 
    def test_connect_prio_state(self):
        c = Connection(hostname='ASA',
                       start=['mock_device_cli --os asa --state asa_disable_pri_act'],
                       os='asa',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        r = c.connect()
        self.assertEqual(r, 'ASA/pri/act>')

    def test_login_connect_ssh(self):
        c = Connection(hostname='ASA',
                            start=['mock_device_cli --os asa --state connect_ssh'],
                            os='asa',
                            credentials=dict(default=dict(username='cisco', password='cisco')))

        r = c.connect()
        self.assertEqual(r, 'Are you sure you want to continue connecting (yes/no)? yes\r\nPassword: cisco\r\nASA#')

    def test_connect_more(self):
        c = Connection(hostname='ASA',
                            start=['mock_device_cli --os asa --state asa_enable_more'],
                            os='asa',
                            credentials=dict(default=dict(username='cisco', password='cisco')),
                            init_exec_commands=['show version'])
        r = c.connect()
        self.assertEqual(r, 'ASA#')

class TestAsaPluginReload(unittest.TestCase):

    def test_asa_reload(self):
        c = Connection(hostname='ASA',
                            start=['mock_device_cli --os asa --state asa_enable'],
                            os='asa',
                            platform='asa',
                            credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        c.reload()

    def test_asav_reload(self):
        c = Connection(hostname='ASA',
                            start=['mock_device_cli --os asa --state asa_reload'],
                            os='asa',
                            platform='asav',
                            credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        c.reload()

class TestAsaPluginExecute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='ASA',
                        start=['mock_device_cli --os asa --state asa_enable'],
                        os='asa',
                        credentials=dict(default=dict(username='cisco', password='cisco')),
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        cls.c.connect()

    def test_execute_error_pattern(self):
        for cmd in ['changeto context GLOBAL', 'network-object host 5.5.50.10', 'display configuration replication warning',
                    'no object-group network TEST_NETWORK']:
            with self.assertRaises(SubCommandFailure) as err:
                r = self.c.execute(cmd)

    def test_error_reporting_pattern(self):
        self.c.execute("error reporting prompt")

    def test_configuration_replication_message(self):
        self.c.execute("display replication message")

    def test_show_version_looks_like_prompt(self):
        v = self.c.execute('show version 2')
        self.assertEqual(v.replace('\r',''), mock_data['asa_enable']['commands']['show version 2']['response'].rstrip())

class TestAsaPluginLearnHostname(unittest.TestCase):

    def test_learn_hostname(self):
        c = Connection(hostname='ASA',
                       start=['mock_device_cli --os asa --state asa_enable --hostname "MyFirewall"'],
                       os='asa',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       init_exec_commands=[],
                       init_config_commands=[],
                       learn_hostname=True
                       )
        c.connect()
        self.assertEqual(c.hostname, 'MyFirewall')


if __name__ == "__main__":
    unittest.main()
