"""
Unittests for SONiC plugin

Uses the mock_device.py script to test the execute service.

"""

__author__ = "Liam Gerrior <lgerrior@cisco.com>"

import os
import yaml
import unittest
from pyats.topology import loader
import unicon
from unicon import Connection
from unicon.core.errors import ConnectionError as UniconConnectionError
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

# currently do not have SONiC specific output to use for mock data
with open(os.path.join(mockdata_path, 'linux/linux_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0


class TestSonicPluginConnect(unittest.TestCase):

    def test_connect_ssh(self):
        c = Connection(hostname='sonic',
                       start=['mock_device_cli --os linux --state connect_ssh'],
                       os='sonic',
                       username='admin',
                       password='cisco')
        c.connect()
        c.disconnect()

    def test_connect_sma(self):
        c = Connection(hostname='sma03',
                       start=['mock_device_cli --os linux --state connect_sma'],
                       os='sonic',
                       username='admin',
                       password='cisco')
        c1 = Connection(hostname='pod-esa01',
                       start=['mock_device_cli --os linux --state connect_sma'],
                       os='sonic',
                       username='admin',
                       password='cisco1')
        c.connect()
        c1.connect()
        c.disconnect()
        c1.disconnect()

    def test_connect_for_password(self):
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os linux --state connect_for_password'],
                       os='sonic',
                       username='admin',
                       password='cisco')
        c.connect()
        c.disconnect()

    def test_bad_connect_for_password(self):
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os linux --state connect_for_password'],
                       os='sonic',
                       username='admin',
                       password='bad_pw')
        with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to agent-lab11-pm'):
            c.connect()

    def test_bad_connect_for_password_credential(self):
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os linux --state connect_for_password'],
                       os='sonic',
                       credentials=dict(default=dict(
                        username='admin', password='bad_pw')))
        with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to agent-lab11-pm'):
            c.connect()

    def test_bad_connect_for_password_credential_no_recovery(self):
        """ Ensure password retry does not happen if a credential fails. """
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os linux --state connect_for_password'],
                       os='sonic',
                       credentials=dict(default=dict(
                        username='admin', password='cisco'),
                        bad=dict(username='baduser', password='bad_pw')),
                       login_creds=['bad', 'default'])
        with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to agent-lab11-pm'):
            c.connect()

    def test_bad_connect_for_password_credential_proper_recovery(self):
        """ Test proper way to try multiple device credentials. """
        c = Connection(hostname='agent-lab11-pm',
            start=['mock_device_cli --os linux --state connect_for_password'],
            os='sonic',
            credentials=dict(default=dict(
             username='admin', password='cisco'),
             bad=dict(username='baduser', password='bad_pw')),
            login_creds=['bad', 'default'])
        try:
            c.connect()
        except UniconConnectionError:
            c.context.login_creds=['default']
            c.connect()

    def test_bad_connect_for_password_credential_proper_recovery_pyats(self):
        """ Test proper way to try multiple device credentials via pyats. """
        testbed = """
        devices:
          agent-lab11-pm:
            type: sonic
            os: sonic
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                command: mock_device_cli --os linux --state connect_for_password
                credentials:
                  default:
                    username: admin
                    password: cisco
                  bad:
                    username: admin
                    password: bad_pw
                login_creds: [bad, default]
        """
        tb=loader.load(testbed)
        l = tb.devices['agent-lab11-pm']
        with self.assertRaises(UniconConnectionError):
            l.connect(connection_timeout=20)
        l.destroy()
        l.connect(login_creds=['default'])
        self.assertEqual(l.is_connected(), True)
        l.disconnect()

    def test_connect_for_login_incorrect(self):
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os linux --state login'],
                       os='sonic',
                       username='cisco',
                       password='wrong_password')
        with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to agent-lab11-pm'):
            c.connect()

    def test_bad_connect_ssh_key(self):
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os linux --state connect_ssh_key_error'],
                       os='sonic')
        with self.assertRaises(UniconConnectionError):
            c.connect()

    def test_connect_hit_enter(self):
        c = Connection(hostname='sonic',
                       start=['mock_device_cli --os linux --state hit_enter'],
                       os='sonic')
        c.connect()
        c.disconnect()

    def test_connect_timeout(self):
        testbed = """
        devices:
          lnx-server:
            type: sonic
            os: sonic
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                command: mock_device_cli --os linux --state login_ssh_delay
        """
        tb=loader.load(testbed)
        l = tb.devices['lnx-server']
        l.connect(connection_timeout=20)
        self.assertEqual(l.is_connected(), True)
        l.disconnect()

    def test_connect_timeout_error(self):
        testbed = """
        devices:
          lnx-server:
            type: sonic
            os: sonic
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                command: mock_device_cli --os linux --state login_ssh_delay
        """
        tb=loader.load(testbed)
        l = tb.devices['lnx-server']
        with self.assertRaises(UniconConnectionError) as err:
            l.connect(connection_timeout=0.5)
        l.disconnect()

    def test_connect_passphrase(self):
        testbed = """
        devices:
          lnx-server:
            type: sonic
            os: sonic
            credentials:
              default:
                username: admin
                password: cisco
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                command: mock_device_cli --os linux --state login_passphrase
        """
        tb=loader.load(testbed)
        l = tb.devices['lnx-server']
        l.connect()

    def test_connect_connectReply(self):
        c = Connection(hostname='sonic',
                       start=['mock_device_cli --os linux --state connect_ssh'],
                       os='sonic',
                       username='admin',
                       password='cisco',
                       connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

    def test_connect_admin_prompt(self):
        c = Connection(hostname='sonic',
                       start=['mock_device_cli --os linux --state linux_password4'],
                       os='sonic',
                       username='admin',
                       password='cisco')
        c.connect()
        c.disconnect()