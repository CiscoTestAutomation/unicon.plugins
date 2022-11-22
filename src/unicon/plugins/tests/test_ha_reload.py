import unittest
from unittest.mock import Mock, call, patch

import unicon
from unicon.mock.mock_device import MockDeviceTcpWrapper
from unicon.plugins.tests.mock.mock_device_ios import MockDeviceTcpWrapperIOS
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE, MockDeviceIOSXE
from unicon.plugins.tests.mock.mock_device_iosxr import MockDeviceTcpWrapperIOSXR
from unicon.plugins.tests.mock.mock_device_nxos import MockDeviceTcpWrapperNXOS, MockDeviceNXOS
from unicon import Connection
from unicon.eal.dialogs import Dialog

class NoInterChangeConsoleMockDeviceIOSXECat9k(MockDeviceIOSXE):
    def cat9k_ha_reload_proceed(self, transport, cmd):
         if 'prompt' in self.transport_ports[self.transport_handles[transport]]:
             prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
             if cmd == "" and prompt == 'Proceed with reload? [confirm]':
                 prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
                 if len(self.transport_ports) > 1 :
                     self.state_change_switchover(
                          transport, 'cat9k_ha_standby_console', 'cat9k_ha_active_console')
                 return True

class NoInterChangeConsoleMockDeviceIOSXEASR(MockDeviceIOSXE):
    def ha_reload_proceed(self, transport, cmd):
         if 'prompt' in self.transport_ports[self.transport_handles[transport]]:
             prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
             if cmd == "" and prompt == 'Proceed with reload? [confirm]':
                 prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
                 if len(self.transport_ports) > 1 :
                     self.state_change_switchover(
                          transport, 'ha_standby_console', 'ha_active_console')
                 return True

class NoInterChangeConsoleMockDeviceNXOS(MockDeviceNXOS):
    def ha_confirm_reload(self, transport, cmd):
         if 'prompt' in self.transport_ports[self.transport_handles[transport]]:
             prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
             if cmd == "y" and prompt == 'This command will reboot the system. (y/n)?  [n]':
                 prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
                 if len(self.transport_ports) > 1 :
                    self.state_change_switchover(
                          transport, 'ha_standby_console', 'ha_active_console')
                 prompt = self.mock_data['ha_active_console']['prompt']
                 self.get_other_transport(transport).write(prompt.encode())
                 return True

class ConfigLockedMockDeviceNXOS(MockDeviceNXOS):
    def __init__(self, *args, **kwargs):
        self.lock_counter = 0
        super().__init__(*args, **kwargs)
    def exec(self, transport, cmd):
        if 'reset counter' in cmd:
            self.lock_counter = int(cmd.split()[-1])
            return True
        if not cmd == 'config term':
            return
        self.mock_data['exec']['commands']['config term'] = "Config mode cannot be entered during Standby initialization."
        if self.lock_counter <= 0:
            self.mock_data['exec']['commands']['config term'] = {'new_state' : 'config'}
        self.lock_counter -= 1


# TBD - IOSXE ASR and Cat9k HA reload unit tests need to be made to work.
"""
class TestHAIOSXEASRReload(unittest.TestCase):
    def setUp(self):
        self.md1 = MockDeviceTcpWrapperIOSXE(port=0, state='asr_exec,asr_exec_standby')
        self.md2 = MockDeviceTcpWrapperIOSXE(port=0, state='asr_exec,asr_exec_standby')
        self.md2.mockdevice = NoInterChangeConsoleMockDeviceIOSXEASR(state='asr_exec,asr_exec_standby')
        self.md1.start()
        self.md2.start()
        self.d1 = Connection(hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(self.md1.ports[0]),
                   'telnet 127.0.0.1 {}'.format(self.md1.ports[1])], username='admin',
            tacacs_password='lab', os='iosxe')
        self.d2 = Connection(hostname='switch',
            start=['telnet 127.0.0.1 {}'.format(self.md2.ports[0]),
                   'telnet 127.0.0.1 {}'.format(self.md2.ports[1])], username='admin',
            tacacs_password='lab', os='iosxe')
        self.d1.connect()
        self.d2.connect()

    def tearDown(self):
        self.md1.stop()
        self.md2.stop()

    def test_reload_console_interchange(self):
        reason=None
        self.d1.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        try:
            self.d1.reload(reload_command='reload')
            result = True
        except Exception as e:
            result = False
            reason = e
        self.assertTrue(result, msg=reason)

    def test_reload(self):
        reason=None
        self.d2.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        try:
            self.d2.reload(reload_command='reload')
            result = True
        except Exception as e:
            result = False
            reason = e
        self.assertTrue(result, msg=reason)

"""


class TestHANXOSReloadConsoleInterchange(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.md = MockDeviceTcpWrapperNXOS(port=0,
                                          state='exec,nxos_exec_standby')
        cls.md.mockdevice = NoInterChangeConsoleMockDeviceNXOS(
            state='exec,nxos_exec_standby')
        cls.md.start()
        cls.d = Connection(
            hostname='switch',
            start=['telnet 127.0.0.1 {}'.format(cls.md.ports[0]),
                   'telnet 127.0.0.1 {}'.format(cls.md.ports[1])],
            username='admin',
            tacacs_password='lab',
            os='nxos'
        )
        cls.d.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDown(cls):
        cls.d.disconnect()
        cls.md.stop()

    def test_reload_console_interchange(self):
        reason = None
        self.d.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        self.d.settings.RELOAD_RECONNECT_WAIT = 1
        try:
            self.d.reload(reload_command='reload')
            result = True
        except Exception as e:
            result = False
            reason = e
        self.assertTrue(result, msg=reason)


class TestNXOSReloadAdminSetup(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.d = Connection(
            hostname='R1',
            start=['mock_device_cli --os nxos --state exec'],
            os='nxos', enable_password='cisco',
            username='admin',
            tacacs_password='lab'
        )
        cls.d.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_reload_repeat_poap_prompt(self):
        reason = None
        self.d.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        self.d.settings.RELOAD_RECONNECT_WAIT = 1
        try:
            self.d.reload(reload_command='reload wr erase')
            result = True
        except Exception as e:
            result = False
            reason = e
        self.assertTrue(result, msg=reason)


class TestNXOSReloadDialog(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.d = Connection(
            hostname='R1',
            start=['mock_device_cli --os nxos --state exec'],
            os='nxos', enable_password='cisco',
            username='admin',
            tacacs_password='lab'
        )
        cls.d.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_ha_reload_dialog_param(self):
        reason = None
        self.d.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        self.d.settings.RELOAD_RECONNECT_WAIT = 1
        dia = Dialog([
            [r'Do you want to proceed with reset operation\? \(y\/n\)\?  \[n\]',
             'sendline(y)', None, True, False]])
        try:
            self.d.reload(reload_command='install reset', dialog=dia)
            result = True
        except Exception as e:
            result = False
            reason = e
        self.assertTrue(result, msg=reason)


class TestHANXOSReloadConfigLock(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.md = MockDeviceTcpWrapperNXOS(port=0,
                                          state='exec,nxos_exec_standby')
        cls.md.mockdevice = ConfigLockedMockDeviceNXOS(
            state='exec,nxos_exec_standby')
        cls.md.start()
        cls.d = Connection(
            hostname='switch',
            start=['telnet 127.0.0.1 {}'.format(cls.md.ports[0]),
                   'telnet 127.0.0.1 {}'.format(cls.md.ports[1])],
            username='admin',
            tacacs_password='lab',
            os='nxos'
        )
        cls.d.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDown(cls):
        cls.d.disconnect()
        cls.md.stop()

    def test_ha_reload_config_lock(self):
        reason = None
        self.d.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        self.d.settings.CONFIG_POST_RELOAD_MAX_RETRIES = 5
        self.d.settings.CONFIG_POST_RELOAD_RETRY_DELAY_SEC = 2
        self.d.settings.RELOAD_RECONNECT_WAIT = 1
        self.d.execute('reset counter 8')
        try:
            self.d.reload('reload')
            result = True
        except Exception as e:
            result = False
            reason = e
        self.d.execute('reset counter 0')
        self.assertTrue(result, msg=reason)


class TestGenericReloadOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = Connection(
            hostname='Router',
            start=['mock_device_cli --os ios --state exec'],
            os='ios', enable_password='cisco',
            username='cisco',
            tacacs_password='cisco'
        )
        md = unicon.mock.mock_device.MockDevice(device_os='ios', state='exec')
        cls.expected_output = md.mock_data['reload_confirm_prompt']['commands']['']['response']
        cls.d.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_reload_output(self):
        self.d.spawn.timeout = 60
        res, output = self.d.reload(return_output=True, target_standby_state='STANDBY')
        self.assertTrue(res)
        self.assertIn(self.expected_output, '\n'.join(output.splitlines()))


class TestHAGenericReloadOutput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ha = MockDeviceTcpWrapperIOS(port=0, state='login,exec_standby')
        md = unicon.mock.mock_device.MockDevice(device_os='ios', state='exec')
        cls.expected_output = md.mock_data['reload_confirm_prompt']['commands']['']['response']
        cls.ha.start()
        cls.ha_device = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 ' + str(cls.ha.ports[0]),
                   'telnet 127.0.0.1 ' + str(cls.ha.ports[1])],
            os='ios', username='cisco', tacacs_password='cisco',
            enable_password='cisco'
        )
        cls.ha_device.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.ha_device.disconnect()
        cls.ha.stop()

    def test_ha_reload_output(self):
        self.ha_device.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        res, output = self.ha_device.reload(return_output=True,
                                            reload_command='reload',
                                            prompt_recovery=True,
                                            timeout=5)
        self.assertTrue(res)
        self.assertIn(self.expected_output, '\n'.join(output.splitlines()))


class TestIosxrHAReloadOutput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ha = MockDeviceTcpWrapperIOSXR(port=0, state='login,enable_standby')
        md = unicon.mock.mock_device.MockDevice(device_os='iosxr', state='exec')
        cls.expected_output = md.mock_data['reload_confirm_prompt']['commands']['']['response']
        cls.ha.start()
        cls.ha_device = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 ' + str(cls.ha.ports[0]),
                   'telnet 127.0.0.1 ' + str(cls.ha.ports[1])],
            os='iosxr',
            username='admin',
            tacacs_password='admin',
        )
        cls.ha_device.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.ha_device.disconnect()
        cls.ha.stop()

    def test_ha_reload_output(self):
        self.ha_device.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        res, output = self.ha_device.reload(return_output=True,
                                            reload_command='reload',
                                            prompt_recovery=True,
                                            target_standby_state='STANDBY',
                                            timeout=30)
        self.assertTrue(res)
        self.assertIn(self.expected_output, '\n'.join(output.splitlines()))


class TestNxosReloadOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = Connection(
            hostname='R1',
            start=['mock_device_cli --os nxos --state exec2 -generic_main'],
            os='nxos', enable_password='cisco',
            credentials=dict(default=dict(
                username='cisco',
                password='cisco'
            ))
        )
        md = unicon.mock.mock_device.MockDevice(device_os='nxos', state='exec')
        cls.expected_output = md.mock_data['login_after_reload']['preface']
        cls.d.connect()
        cls.d.settings.POST_RELOAD_WAIT = 1

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_nxos_reload_output(self):
        res, output = self.d.reload(return_output=True)
        self.assertTrue(res)
        self.assertTrue(self.expected_output in output.replace('\r', ''))


class TestHANxosReloadOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperNXOS(port=0,
                                          state='exec,nxos_exec_standby')
        cls.md.mockdevice = NoInterChangeConsoleMockDeviceNXOS(
            state='exec,nxos_exec_standby')
        cls.md.start()
        md = unicon.mock.mock_device.MockDevice(device_os='nxos', state='exec')
        cls.expected_output = md.mock_data['ha_active_console']['preface']
        cls.ha_device = Connection(
            hostname='switch',
            start=['telnet 127.0.0.1 {}'.format(cls.md.ports[0]),
                   'telnet 127.0.0.1 {}'.format(cls.md.ports[1])],
            username='admin',
            tacacs_password='lab', os='nxos'
        )
        cls.ha_device.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.ha_device.disconnect()
        cls.md.stop()

    def test_nxos_ha_reload_output(self):
        self.ha_device.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        res, output = self.ha_device.reload(return_output=True)
        self.assertTrue(res)
        self.assertIn(self.expected_output, '\n'.join(output.splitlines()))


class TestIosXECat3kReloadOutput(unittest.TestCase):
    def test_iosxecat3k_reload_output(self):
        d = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe --state cat3k_exec'],
            os='iosxe',
            platform='cat3k',
            line_password='lab',
            enable_password='lab'
        )
        d.connect()
        md = unicon.mock.mock_device.MockDevice(device_os='iosxe',
                                                state='cat3k_exec')
        expected_output = md.mock_data['reload_cat3k_logs']['prompt']
        res, output = d.reload(return_output=True)
        self.assertTrue(res)
        self.assertIn(expected_output.strip('\n'),
                      '\n'.join(output.splitlines()))

if __name__ == "__main__":
    unittest.main()