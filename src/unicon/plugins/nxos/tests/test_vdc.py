"""
    This test module implements all the tests required for VDC validation.
    The tests are from black-box perspective and requires a device.

    Few tests are being tested implicitly.
    - Creation of VDC
"""
import unittest
from unicon.utils import AttributeDict
from unicon import Connection
from unicon.core.errors import SubCommandFailure

device = AttributeDict({
    'start': ['telnet 10.64.70.24 2020', 'telnet 10.64.70.24 2019'],
    'hostname': 'step-n7k-2',
    'tacacs_username': 'admin',
    'tacacs_password': r'Cscats123!',
    'os': 'nxos'
})

class TestVdc(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """create a connection with the device"""
        cls.con = Connection(hostname=device.hostname,
                         start=device.start,
                         os=device.os,
                         tacacs_username=device.tacacs_username,
                         tacacs_password=device.tacacs_password)
        cls.con.connect()
        cls.con.configure("license grace-period")
        cls.vdcs = AttributeDict({
            "vdc1": "vdc1",
            "vdc2": "vdc2",
            "vdc3": "vdc3"
        })
        # store the name of vdcs for reference in the program.

    @classmethod
    def tearDownClass(cls):
        cls.con.disconnect()

    def setUp(self):
        """create the vdcs if they dont exist"""
        vdcs_on_device = self.con.list_vdc()
        for vdc in self.vdcs:
            if vdc not in vdcs_on_device:
                self.con.create_vdc(vdc)

    def test_list_vdc(self):
        """return should be of type list"""
        vdc_list = self.con.list_vdc()
        self.assertIsInstance(vdc_list, list)

    def test_hostname_in_vdc_list(self):
        """vdc list must contain the hostname"""
        vdc_list = self.con.list_vdc()
        self.assertIn(self.con.hostname, vdc_list)

    def test_list_vdc_from_vdc_mode(self):
        """test if list_vdc can be executed when device is already in the
        vdc mode. device must return to the initial vdc after executing the
        command
        """
        self.con.switchto(self.vdcs.vdc1)
        self.con.list_vdc()
        self.assertEqual(self.con.current_vdc, self.vdcs.vdc1)
        self.con.switchback()

    def test_switch_to_vdc(self):
        """simply switch to and existing vdc"""
        self.con.switchto(self.vdcs.vdc1)
        self.con.switchback()

    def test_switch_vdc_from_vdc(self):
        """switch to vdc while device is in another vdc"""
        self.con.switchto(self.vdcs.vdc1)
        self.con.switchto(self.vdcs.vdc2)
        self.assertEqual(self.con.current_vdc, self.vdcs.vdc2)
        self.con.switchback()

    def test_switch_to_non_existent_vdc_1(self):
        """switch to a vdc which doesnt exist"""
        with self.assertRaises(SubCommandFailure):
            self.con.switchto("does_not_exists")

    def test_switch_to_non_existent_vdc_2(self):
        """switch to a vdc which doesnt exist from a different vdc"""
        self.con.switchto(self.vdcs.vdc1)
        with self.assertRaises(SubCommandFailure):
            self.con.switchto("does_not_exists")
        self.assertEqual(self.con.current_vdc, self.vdcs.vdc1)
        self.con.switchback()

    def test_switch_to_same_vdc(self):
        """switch to the same vdc on which device is currently present"""
        self.con.switchto(self.vdcs.vdc1)
        self.con.switchto(self.vdcs.vdc1)
        self.con.switchback()

    def test_delete_vdc(self):
        """simple case, delete vdc from default vdc"""
        self.con.delete_vdc(self.vdcs.vdc1)
        self.assertNotIn(self.vdcs.vdc1, self.con.list_vdc())

    def test_delete_current_vdc(self):
        """delete current vdc"""
        self.con.switchto(self.vdcs.vdc2)
        with self.assertRaises(SubCommandFailure):
            self.con.delete_vdc(self.vdcs.vdc2)
        self.con.switchback()

    def test_delete_vdc_from_vdc(self):
        """delete a vdc from being in a different vdc"""
        self.con.switchto(self.vdcs.vdc2)
        self.con.delete_vdc(self.vdcs.vdc3)
        self.assertEqual(self.con.current_vdc, self.vdcs.vdc2)
        self.con.switchback()

    def test_switchback(self):
        """switch back from a vdc"""
        self.con.switchto(self.vdcs.vdc1)
        self.con.switchback()
        self.assertEqual(self.con.current_vdc, None)

    def test_switchback_from_default_vdc(self):
        """test switchback when device is already in default vdc"""
        self.con.switchback()

    def create_vdc_which_exists(self):
        """create a vdc which already exists"""
        with self.assertRaises(SubCommandFailure):
            self.con.create_vdc(self.vdcs.vdc1)

    def create_vdc_from_some_other_vdc(self):
        """create vdc from device being in some other vdc"""
        self.con.switchto(self.vdcs.vdc1)
        self.con.create_vdc('random')
        self.assertEqual(self.con.current_vdc, self.vdcs.vdc1)
        self.con.delete_vdc('random')
        self.con.switchback()

    def test_disconnect(self):
        """disconnect should switchback if needed"""
        self.con.disconnect()
        self.assertEqual(self.con.current_vdc, None)
        self.con.connect()

    def test_create_vdc_when_not_allowed(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)