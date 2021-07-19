
import unittest
from unittest.mock import Mock, patch
from time import sleep

import unicon
from unicon import Connection
from pyats.topology import loader
from unicon.eal.dialogs import Statement
from unicon.plugins.iosxe.service_implementation import Copy

from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEPluginHAConnect(unittest.TestCase):
    """ Run unit testing on a mocked IOSXE ASR HA device """

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXE(
            port=0, state='asr_login,asr_exec_standby')
        cls.md.start()

        cls.testbed = """
        devices:
          Router:
            os: iosxe
            type: router
            tacacs:
                username: cisco
            passwords:
                tacacs: cisco
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
        """.format(cls.md.ports[0], cls.md.ports[1])

    @classmethod
    def tearDownClass(cls):
        cls.md.stop()


    def test_connect(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.connect()
        r.disconnect()

    def test_switchover(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.connect()
        asm = r.active.state_machine

        # The mocked active device immediately switches over to
        # disable mode on switchover, so ensure the dialog exits if this
        # pattern is detected.
        #
        # The reason we want this behavior is that the mocked device
        # currently does not simulate a reset cycle (in which the
        # disable state on the newly standby is a transitory state
        # seen just before reload).
        asm.add_default_statements(Statement(
            pattern=asm.get_state('disable').pattern,loop_continue=False))
        r.switchover()
        r.disconnect()

    def test_copy(self):
        tb = loader.load(self.testbed)
        dev = tb.devices.Router
        dev.connect()
        self.assertEqual(isinstance(dev.copy, Copy), True)
        dev.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEPluginSwitchoverWithStandbyCredentials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe --state c9k_login3'],
            os='iosxe',
            credentials=dict(
                default=dict(
                    username='admin', password='cisco'),
                enable=dict(
                    username='admin', password='cisco'),
                disable=dict(
                    username='admin', password='cisco')))
        cls.c.connect()

    def test_switchover(self):
        self.c.execute('redundancy force-switchover')

if __name__ == "__main__":
    unittest.main()
