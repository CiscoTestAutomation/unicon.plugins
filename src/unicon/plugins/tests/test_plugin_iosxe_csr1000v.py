
import unittest

from unicon import Connection


class TestIosXEConfigure(unittest.TestCase):

    def test_config_no_service_prompt_config(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state enable_no_service_prompt_config'],
                       os='iosxe',
                       platform='csr100v',
                       init_exec_commands=[],
                       init_config_commands=[],
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True
                       )
        c.connect()
        c.configure(['no logging console'])
        c.disconnect()


if __name__ == "__main__":
    unittest.main()
