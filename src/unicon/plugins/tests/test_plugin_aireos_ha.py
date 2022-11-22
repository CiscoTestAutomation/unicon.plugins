

from time import sleep

import unittest
from unittest.mock import Mock, patch

import unicon
from pyats.topology import loader

from unicon.plugins.tests.mock.mock_device_aireos import MockDeviceTcpWrapperAireos


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
        tb = loader.load(cls.testbed)
        cls.wlc = tb.devices['WLC']
        cls.wlc.connect(settings=dict(POST_DISCONNECT_WAIT_SEC=0,
                                      GRACEFUL_DISCONNECT_WAIT_SEC=0))

    @classmethod
    def tearDownClass(cls):
        cls.wlc.disconnect()
        cls.md.stop()

    def test_save_config(self):
        self.wlc.execute('save config')

if __name__ == "__main__":
    unittest.main()
    
