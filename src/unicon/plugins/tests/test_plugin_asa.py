"""
Unittests for asa plugin

Uses the mock_device.py script to test the plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import os
import re
import yaml
import unittest


import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.mock.mock_device import mockdata_path
from unicon.plugins.utils import sanitize

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
        self.assertEqual(r.replace('\r', ''), """\
ASA/pri/act>
enable
Password: cisco
ASA/pri/act#
terminal pager 0
ASA/pri/act#
""")

    def test_login_connect_ssh(self):
        c = Connection(hostname='ASA',
                       start=['mock_device_cli --os asa --state connect_ssh'],
                       os='asa',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        r = c.connect()
        # Need to sanitize strings because due to the timing and stripping of log messages
        # in the connect return string, sometimes empty lines can be inserted into the output
        # at different places
        self.assertEqual(sanitize(r.replace('\r', '')), sanitize("""\
The authenticity of host '127.0.0.1 (127.0.0.1)' can't be established.
RSA key fingerprint is a1:07:ac:9b:8c:c2:db:c5:4c:dc:70:b5:09:2a:a5:b1.

Are you sure you want to continue connecting (yes/no)? yes
Password: cisco
ASA#
terminal pager 0
ASA#
"""))

    def test_connect_more(self):
        c = Connection(hostname='ASA',
                       start=['mock_device_cli --os asa --state asa_enable_more'],
                       os='asa',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       init_exec_commands=['show version'])
        r = c.connect()
        # Need to sanitize strings because due to the timing and stripping of log messages
        # in the connect return string, sometimes empty lines can be inserted into the output
        # at different places
        self.assertEqual(sanitize(r.replace('\r', '')), sanitize("""\
ASA#
show version
Cisco Adaptive Security Appliance Software Version 9.8(3)235
Firepower Extensible Operating System Version 2.2(2.100)
Device Manager Version 7.9(2)152

Compiled on Thu 27-Sep-18 14:58 PDT by builders
System image file is "disk0:/mnt/boot/installables/switch/fxos-k8-fp2k-npu.2.2.2.100.SPA"
Config file at boot was "startup-config"

FP2130-LK1-FP2130 up 10 hours 51 mins
failover cluster up 1 day 9 hours

Hardware:   FPR-2130, 14852 MB RAM, CPU MIPS 1200 MHz, 1 CPU (12 cores)

1: Int: Internal-Data0/1    : address is 000f.b748.4800, irq 0
3: Ext: Management1/1       : address is d4e8.80b7.4381, irq 0
4: Int: Internal-Data1/1    : address is 0000.0100.0001, irq 0

License mode: Smart Licensing
License reservation: Enabled

Licensed features for this platform:
Maximum Physical Interfaces       : Unlimited
Maximum VLANs                     : 1024
Inside Hosts                      : Unlimited
Failover                          : Active/Active
Encryption-DES                    : Enabled
Encryption-3DES-AES               : Enabled
Security Contexts                 : 2
Carrier                           : Disabled
<--- More ---> 
ASA#
"""))


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
