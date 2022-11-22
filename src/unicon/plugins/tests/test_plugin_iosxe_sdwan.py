import unittest
from unittest.mock import patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog, Statement
from unicon.core.errors import SubCommandFailure, StateMachineError, UniconAuthenticationError, ConnectionError as UniconConnectionError
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXESdwanConnect(unittest.TestCase):

   def test_iosxe_sdwan_connect(self):
        testbed = '''
            devices:
              Router:
                type: router
                os: iosxe
                platform: sdwan
                credentials:
                    default:
                        username: cisco
                        password: cisco
                connections:
                  defaults:
                    class: 'unicon.Unicon'
                  cli:
                    command: mock_device_cli --os iosxe --state sdwan_banner_password
        '''
        t = loader.load(testbed)
        d = t.devices.Router
        try:
            d.connect()
        finally:
            d.disconnect()


class TestIosXESDWANConfigure(unittest.TestCase):

    def test_config_transaction(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable'],
                       os='iosxe', platform='sdwan',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )

        try:
            d.connect()
            d.configure('no logging console')
        finally:
            d.disconnect()

    def test_config_transaction_sdwan_iosxe(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable'],
                       os='sdwan', platform='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )

        try:
            d.connect()
            d.configure('no logging console')
        finally:
            d.disconnect()

    def test_config_transaction_sdwan_iosxe_confirm(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable2'],
                       os='iosxe', platform='sdwan',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True,
                       mit=True
                       )

        try:
            d.connect()
            d.configure('no logging console')
        finally:
            d.disconnect()


if __name__ == "__main__":
    unittest.main()
