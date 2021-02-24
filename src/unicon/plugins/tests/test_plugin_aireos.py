"""
Unittests for aireos plugin

"""

import re
import unittest
from unittest.mock import patch

from unicon.core.errors import SubCommandFailure
from unicon import log, Connection
import unicon

box = dict()
hostname = 'Cisco Capwap Simulator'
box['hostname'] = hostname
box['username'] = 'lab'
box['tacacs_password'] = 'lab'
box['cmd'] = 'mock_device_cli --os aireos  --state aireos_exec --hostname "{}"'.format(hostname)

ping_failure = '192.168.2.3'

tftp_server = '172.118.0.3'
simconf_file = '/thvegas/ble_vegas'
img_file = '/thvegas/SIM_5500_8_2_1_114.aes'


def get_dev():
    dev = Connection(hostname=box['hostname'],
                     username=box['username'],
                     tacacs_password=box['tacacs_password'],
                     start=[box['cmd']], 
                     os='aireos')
    dev.connect()
    return dev


def execute_show(dev):
    stats = dev.execute("show memory statistics")
    ret = True
    if not re.search(r'Total System Memory', stats):
        ret = False
    if not re.search(r'System Memory Statistics', stats):
        ret = False
    return ret


class TestAireos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        log.info('Testing aireos plugin')
        global device
        device = get_dev()

    @classmethod
    def tearDownClass(cls):
        device.disconnect()

    def setUp(self):
        self.device = device

    def test_service_init_after_connect(self):
        self.assertEqual(self.device._service_init, True)

    # def test_ping(self):
    #     self.device.ping(addr="127.0.0.1")

    # def test_ping_invalid_format(self):
    #     with self.assertRaises(SubCommandFailure):
    #         self.device.ping(addr="1.0.2")

    # def test_ping_failed(self):
    #     with self.assertRaises(SubCommandFailure):
    #         self.device.ping(addr=ping_failure)

    # def test_ping_end_state(self):
    #     self.device.ping(addr="127.0.0.1")
    #     self.assertEqual(self.device.ping.end_state, 'enable')

    # def test_execute(self):
    #     self.assertEqual(execute_show(self.device), True)

    def test_config(self):
        ret = self.device.configure("paging disable")
        ret = ret.strip()
        self.assertEqual(ret, "paging disable")

    def test_config_error(self):
        conf = self.device.configure("paging mistake")
        ret = True
        if not re.search(r'wrong argument for paging', conf):
            ret = False
        self.assertEqual(ret, True)


def reconnect_dev(dev):
    dev.disconnect()
    dev = get_dev()
    return dev


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestAireosLoginStateMachine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        log.info('Testing aireos plugin login states')

    def setUp(self):
        self.device = get_dev()

    def tearDown(self):
        self.device.disconnect()

    # def test_login_from_cat_eof(self):
    #     self.device.sendline('devshell shell')
    #     self.device.expect(['#'])
    #     self.device.sendline('cat <<MY_EOF >/dev/null')
    #     self.device = reconnect_dev(self.device)
    #     self.assertEqual(execute_show(self.device), True)

    # def test_login_from_shell(self):
    #     self.device.sendline('devshell shell')
    #     self.device.expect(['#'])
    #     self.device = reconnect_dev(self.device)
    #     self.assertEqual(execute_show(self.device), True)

    def test_login_from_show(self):
        self.device.sendline('show')
        self.device = reconnect_dev(self.device)
        # self.assertEqual(execute_show(self.device), True)


class TestAireosReboots(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        log.info('Testing aireos TSIM reloads/transfer')
        global device
        device = get_dev()

    @classmethod
    def tearDownClass(cls):
        device.disconnect()

    def setUp(self):
        self.device = device

    def test_reload(self):
        self.device.reload()
        # self.assertEqual(execute_show(self.device), True)

    # reload with error patterns in the mock data
    def test_reload_with_errors(self):
        with self.assertRaises(SubCommandFailure) as err:
            self.device.reload("reset system forced with errors")
        device.disconnect()

    def test_transfer_simconf_devshell(self):
        simconf = """
AP_BASE_MAC=00:0b:0c
MS_BASE_MAC=00:00:0a:04
TEST_DEVICE=TALWAR
NUM_HOSTS=250
AP_NAME=MYAP
WLAN_SSID=test_wlan,1,3000;
MS_STATIC_SUBNETS_LIST=9.0.0.2,255.255.0.0,9.0.0.1,3000;
CLIENT_DHCP_SUPPORT=1
AP_HOST_DIST_LIST=250,3000,10.0.0.2,10.0.0.1,204c.9e3e.2856,1,0,10.0.0.1,,,1    0.0.0.1,TALWAR,US
ENABLE_ROGUE_REPORT=1
ROGUE_AP_MAC=00:00:7a:30
ROGUE_CLIENT_MAC=00:00:8a:30
ROGUE_AP_PER_AP=5
ROGUE_CLIENT_PER_AP=6
SEC_MODE=OPEN,1;
ENABLE_CDP=1
RFIDTAG=0;
RFID_BASE_MAC=00:00:3a:43;
NUM_RFID_TAGS=5000;
RFID_REPEAT=3;
RFID_BEACON_INTERVAL=60;
RFID_TAG_TYPE=CISCO;
RFID_CHANNELS=3,1,6,11;
LOCATION_OPTIONS=CISCO,XY,TEXT,NORMAL,NA,1;
LOCATION_ONDEMAND_INTERVAL=30;
INTF_DEV=IBEACON,5;
AP_JOIN_CHANNELS=1,36;
MAX_LOCATION=10
IBEACON_UUID=aa4cbc02cc06dd15ee01ff0a03
"""
        self.device.copy(config=simconf)
        # self.assertEqual(execute_show(self.device), True)

    def test_transfer_simconf_no_source_file(self):
        with self.assertRaises(SubCommandFailure):
            self.device.copy(mode='simconfig',
                             server=tftp_server)

    def test_transfer_simconf_no_server(self):
        with self.assertRaises(SubCommandFailure):
            self.device.copy(source_file=simconf_file,
                             mode='simconfig')

    @unittest.skip("Needs a tftp server")
    def test_transfer_simconf_tftp(self):
        self.device.copy(source_file=simconf_file,
                         mode='simconfig',
                         server=tftp_server)
        # self.assertEqual(execute_show(self.device), True)

    @unittest.skip("Needs a tftp server")
    def test_transfer_image_tftp(self):
        self.device.copy(source_file=img_file,
                         server=tftp_server)
        # self.assertEqual(execute_show(self.device), True)


class TestAireOsPlugin(unittest.TestCase):

    def setUp(self):
        self.c = Connection(hostname='Cisco Capwap Simulator',
                            start=['mock_device_cli --os aireos  --state aireos_exec --hostname "{}"'.format(hostname)],
                            os='aireos',
                            username='lab')
        self.cc = Connection(hostname='Cisco Capwap Simulator',
                             start=['mock_device_cli --os aireos  --state aireos_exec --hostname "{}"'.format(hostname)],
                             os='aireos',
                             credentials=dict(default=dict(username='lab', password='lab')))

    def test_connect(self):
        self.c.connect()

    def test_reload(self):
        self.c.connect()
        self.c.reload()

    def test_reload_credentials(self):
        self.cc.connect()
        self.cc.reload()

    def test_restart(self):
        self.c.connect()
        self.c.reload("restart")

    def test_force_switchover(self):
        self.c.connect()
        self.c.reload("redundancy force-switchover")

    def test_press_any_key(self):
        self.c.connect()
        self.c.execute("grep exclude generation 'show run-config startup-commands'")

    def test_press_enter_key(self):
        self.c.connect()
        self.c.execute("show run-config")

    def test_more(self):
        self.c.connect()
        self.c.execute("show command with more")

    def test_execute_error_pattern(self):
        for cmd in ['transfer upload start', 'show foo', 'debug lwapp', 'config time ntp delete foo',
                    'config time ntp delete 2', 'config wlan enable 20', 'config wlan security web-auth captive-bypass enable 10',
                    'config wlan error', 'config wlan interface 511 all-interfaces', 'config wlan create 511 Company-guest Company-guest']:
            with self.assertRaises(SubCommandFailure) as err:
                r = self.c.execute(cmd)

    def test_save_config(self):
        self.c.connect()
        self.c.execute('save config')

class TestAireOsPluginLearnHostname(unittest.TestCase):
    def test_learn_hostname(self):
        c = Connection(hostname='Controller',
                       start=['mock_device_cli --os aireos  --state aireos_exec --hostname "{}"'.format(hostname)],
                       os='aireos',
                       username='lab',
                       learn_hostname=True,
                       connection_timeout=3)
        c.connect()


class TestAireosPluginStates(unittest.TestCase):

    def setUp(self):
        self.c = Connection(hostname='Controller',
                            start=['mock_device_cli --os aireos  --state aireos_exec --hostname Controller'],
                            os='aireos',
                            username='lab',
                            init_config_commands=[])
        self.c.connect()

    def test_all_states(self):
        states = ['show', 'test', 'debug', 'transfer', 'license', 'reset', 'save', 'shell']
        for state in states:
            self.c.log.info('Changing to state %s' % state)
            self.c.state_machine.go_to(state, self.c.spawn)
            self.assertEqual(self.c.state_machine.current_state, state)


class TestAireosPluginConnect(unittest.TestCase):

    def test_connect_with_capwap_sim(self):
        c = Connection(hostname='Controller',
                            start=['mock_device_cli --os aireos  --state aireos_exec --hostname "Cisco Capwap Simulator"'],
                            os='aireos',
                            username='lab',
                            init_config_commands=[])
        c.connect()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
