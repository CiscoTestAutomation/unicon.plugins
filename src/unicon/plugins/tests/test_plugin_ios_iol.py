import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.plugins.tests.mock.mock_device_ios import MockDeviceTcpWrapperIOS


class TestIosIolPluginHASwitchover(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.ha = MockDeviceTcpWrapperIOS(port=0, state='enable,exec_standby2')
        cls.ha.start()
        cls.d_ha = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 ' + str(cls.ha.ports[0]),
                   'telnet 127.0.0.1 ' + str(cls.ha.ports[1])],
            os='ios',
            series='iol',
            username='cisco',
            tacacs_password='cisco',
            enable_password='cisco',
        )
        try:
            cls.d_ha.connect()
        except Exception:
            cls.ha.stop()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
    def tearDown(cls):
        cls.d_ha.disconnect()
        cls.ha.stop()

    def test_switchover(self):
        self.d_ha.switchover()


if __name__ == '__main__':
    unittest.main()
