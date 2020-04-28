

from time import sleep

import unittest
from unittest.mock import Mock, patch

import unicon
from pyats.topology import loader

from unicon.plugins.tests.mock.mock_device_aireos import MockDeviceTcpWrapperAireos


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestAireosPluginHAConnect(unittest.TestCase):
    """ Run unit testing on a mocked AireOS HA device """

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperAireos(
            port=0, state='aireos_exec,aireos_exec_standby', hostname='WLC')
        cls.md.start()

        cls.testbed = """
        devices:
          WLC:
            os: aireos
            type: wlc
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
        wlc = tb.devices['WLC']
        wlc.connect()
        wlc.disconnect()
