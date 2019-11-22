
import unittest
from time import sleep

from unicon import Connection
from pyats.topology import loader

from unicon.plugins.tests.mock.mock_device_iosxr import MockDeviceTcpWrapperIOSXR


class TestIOSXRPluginHAConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXR(port=0, state='login,console_standby')
        cls.md.start()

        cls.testbed = """
        devices:
          Router:
            os: iosxr
            type: router
            tacacs:
                username: admin
            passwords:
                tacacs: admin
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
        cls.r = tb.devices.Router
        cls.r.connect()

    @classmethod
    def tearDownClass(self):
        self.md.stop()

    def test_execute(self):
        self.r.execute('show platform')

    def test_switchover(self):
        self.r.switchover(sync_standby=False)

    def test_switchover_with_standby_sync(self):
        self.r.switchover(sync_standby=True)

    def test_bash_console(self):
        with self.r.bash_console() as conn:
            conn.execute('pwd')
        ret = self.r.active.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)

    def test_attach_console(self):
        with self.r.attach_console('0/RP0/CPU0') as conn:
            conn.execute('ls')
        ret = self.r.active.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)

class TestIOSXRPluginHAConnectAdmin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXR(port=0, state='login1,console_standby')
        cls.md.start()

        cls.testbed = """
        devices:
          Router:
            os: iosxr
            type: router
            tacacs:
                username: admin
            passwords:
                tacacs: admin
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
        cls.r = tb.devices.Router
        cls.r.connect()

    @classmethod
    def tearDownClass(self):
        self.md.stop()

    def test_admin_attach_console(self):

        with self.r.admin_attach_console('0/RP0') as console:
            out = console.execute('pwd')
            self.assertIn('/misc/disk1', out)
        ret = self.r.active.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)


if __name__ == "__main__":
    unittest.main()
