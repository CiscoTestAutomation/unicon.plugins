import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestISEPluginConnect(unittest.TestCase):

    def test_connect_resume(self):
        c = Connection(hostname='dc-ise-1',
                       start=['mock_device_cli --os ise --state ise_resume_session'],
                       os='ise')
        c.connect()
        c.disconnect()


if __name__ == "__main__":
    unittest.main()
