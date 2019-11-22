import unittest
import re
from unicon.core.errors import SubCommandFailure
from unicon import log, Connection

############################################
# Please change follow parameters as needed
name = "sprasads-ise1"
username = "admin"
password = "Lab123"
start = "ssh 10.106.142.210"
############################################

os = "ise"
chassis_type = "single_rp"

def get_dev():
    dev = Connection(hostname=name,
                     username=username,
                     password=password,
                     start=[start],
                     os=os)
    dev.connect()
    return dev

def reconnect_dev(dev):
    dev.disconnect()
    dev = get_dev()
    return dev


def execute_show(dev):
    stats = dev.execute("term length 0")
    stats = dev.execute("show version")
    ret = True
    if not re.search(r'Cisco Identity Services Engine', stats):
        ret = False
    return ret

class TestIse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        log.info('Testing ise plugin')
        global device
        device = get_dev()

    @classmethod
    def tearDownClass(cls):
        device.disconnect()

    def setUp(self):
        self.device = device

    def test_service_init_after_connect(self):
        self.assertEqual(self.device._service_init, True)

    def test_execute_without_cmd(self):
        with self.assertRaises(TypeError):
            self.device.execute()

    def test_execute_with_timeout(self):
        self.device.execute("sh clock", timeout=5)

    def test_execute_with_timeout(self):
        with self.assertRaises(SubCommandFailure):
            self.device.execute("sh app statu ise", timeout=1)

    def test_state_after_execute(self):
        self.device.execute("sh clock")
        self.assertEqual(self.device.state_machine._current_state, 'shell')

    def test_config_with_no_cmd(self):
        self.device.configure()

    def test_execute(self):
        self.assertEqual(execute_show(self.device), True)

    def test_config(self):
        ret = self.device.configure("cdp timer 80")
        self.assertEqual(self.device.state_machine._current_state, 'shell')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
