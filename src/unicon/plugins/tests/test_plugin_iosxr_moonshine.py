"""
Unittests for IOSXR moonshine plugin

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.plugins.tests.mock.mock_device_iosxr import MockDeviceTcpWrapperIOSXR
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXrMoonshinePlugin(unittest.TestCase):

    def test_connect(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxr --state moonshine_enable'],
                       os='iosxr',
                       platform='moonshine',
                       credentials=dict(default=dict(username='admin', password='admin')))
        try:
            c.connect()
        finally:
            c.disconnect()

    def test_connect_ha(self):
        c = Connection(hostname='Router',
                       start=[
                            'mock_device_cli --os iosxr --state moonshine_enable',
                            'mock_device_cli --os iosxr --state moonshine_enable_standby',
                       ],
                       os='iosxr',
                       platform='moonshine',
                       credentials=dict(default=dict(username='admin', password='admin')))
        try:
            c.connect()
        finally:
            c.disconnect()

    def test_connect_ha2(self):
        c = Connection(hostname='Router',
                       start=[
                            'mock_device_cli --os iosxr --state moonshine_enable_standby',
                            'mock_device_cli --os iosxr --state moonshine_enable',
                       ],
                       os='iosxr',
                       platform='moonshine',
                       credentials=dict(default=dict(username='admin', password='admin')))
        try:
            c.connect()
        finally:
            c.disconnect()


class TestIosXrConfigPrompts(unittest.TestCase):
    """Tests for config prompt handling."""

    @classmethod
    def setUpClass(cls):
        cls._moonshine_conn = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state moonshine_enable'],
            os='iosxr',
            platform='moonshine',
        )
        cls._moonshine_conn.connect()

    @classmethod
    def tearDownClass(cls):
        cls._moonshine_conn.disconnect()

    def test_failed_config_moonshine(self):
        """Check that we can successfully return to an enable prompt after entering failed config on moonshine."""
        self._moonshine_conn.execute("configure terminal", allow_state_change=True)
        self._moonshine_conn.execute("test failed")
        self._moonshine_conn.spawn.timeout = 60
        self._moonshine_conn.enable()
