__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"


import unittest
from unicon import Connection

############################################
# Please change follow parameters as needed
name = "E5-37-C3850"
username = "lab"
password = "lab"
start = "telnet 10.51.66.5 2013"
tftp_image = "tftp://172.18.200.210/BB_IMAGES/polaris_dev/rp_super_universalk9.edison.bin"
############################################

os = "iosxe"
chassis_type = "single_rp"
platform = "cat3k"


class TestIosXE(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con = Connection(hostname=name,
                             username=username,
                             tacacs_password=password,
                             start=[start],
                             os=os,
                             platform=platform)
        cls.con.connect()

    @classmethod
    def tearDownClass(cls):
        cls.con.disconnect()

    def test_linux_exec(self):
        output = self.con.shellexec("whoami")
        assert output == "root"
        assert self.con.state_machine.current_state == "enable"

    def test_reload_1(self):
        self.con.config("boot manual")
        self.con.reload(image_to_boot=tftp_image, timeout=1200)
        assert self.con.state_machine.current_state == "enable"

    def test_reload_2(self):
        self.con.config("no boot manual")
        self.con.config("boot system {}".format(tftp_image))
        self.con.reload(timeout=1200)
        assert self.con.state_machine.current_state == "enable"

    def test_delete_file(self):
        filename = "i_should_not_be_here"
        self.con.shellexec("touch /flash/{}".format(filename))
        self.con.execute("delete flash:{}".format(filename))
        assert "No such file or directory" in \
               self.con.shellexec("ls /flash/{}".format(filename))

    def test_write_erase(self):
        self.con.execute("write erase")
        self.con.copy(source="running-conf", dest="startup-config")

    def test_rommon(self):
        self.con.execute("show ip interface brief")
        self.con.rommon("MANUAL_BOOT=yes", end_state="rommon")
        self.con.rommon("set", end_state="enable" )
        self.con.execute("show ip interface brief")
