"""
Unittest for copy() service
"""

import re
import unittest
import unicon
from unittest.mock import patch

from unicon import Connection, eal
from unicon.mock import mock_device
from unicon.core.errors import SubCommandFailure, TimeoutError
from unicon.plugins.tests.mock.mock_device_ios import MockDeviceIOS, MockDeviceTcpWrapperIOS
from unicon.utils import to_plaintext, SecretString

class NetworkCopyFailMockDevice(MockDeviceIOS):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.copy_count = 1
        self.max_copy_fail = 3
        self.org_copy_response = self.mock_data['serv_prompt']['commands']['10.1.0.207']['response'] 
    def serv_prompt(self, transport, cmd):
        if self.copy_count < self.max_copy_fail:
            self.mock_data['serv_prompt']['commands'][cmd]['response'] = 'Trying to connect to tftp server.....\nConnection to Server Established.\n[###################] 0  KB TFTP Timed out.'
            self.copy_count = self.copy_count + 1
        else:
            self.mock_data['serv_prompt']['commands'][cmd]['response'] = self.org_copy_response


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestCopyService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = Connection(hostname='Router', 
                        start=['mock_device_cli --os ios --state exec'],
                        os='ios',
                        username='cisco',
                        tacacs_password='cisco',
                        enable_password='cisco')
        cls.d.connect()
        cls.md = mock_device.MockDevice(device_os='ios', state='exec')

    @classmethod
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_copy_from_flash(self):
        test_output = self.d.copy(source = 'flash:', dest = 'flash-3:',
                          source_file = '/cat3k_caa-universalk9.bld_polaris.bin',
                          dest_file = '/cat3k_caa-universalk9.bld_polaris.bin',
                          timeout = 9)
        expected_output = self.md.mock_data['dest_file']['commands']\
                              ['/cat3k_caa-universalk9.bld_polaris.bin']['response']
        test_output = '\n'.join(test_output.splitlines())
        expected_output = '\n'.join(expected_output.splitlines())
        self.assertIn(expected_output, test_output)

    def test_copy_tftp(self):
        test_output = self.d.copy(source = 'tftp:', dest = 'bootflash:',
                          source_file = '/tftpboot/mdear/n7k.gbin' ,
                          server = '10.1.0.207', user = 'rcpuser' ,
                          password = '123rcp!', vrf = 'management',
                          timeout = 9)
        expected_output = self.md.mock_data['serv_prompt']['commands']\
                              ['10.1.0.207']['response']
        test_output = '\n'.join(test_output.splitlines())
        expected_output = '\n'.join(expected_output.splitlines())
        self.assertIn(expected_output, test_output)

    def test_copy_ftp_secret_password(self):
        test_output = self.d.copy(source = 'ftp:', dest = 'bootflash:',
                          source_file = '/tftpboot/mdear/n7k.gbin' ,
                          server = '10.1.0.207', user = 'rcpuser' ,
                          password = SecretString.from_plaintext('123rcp!'),
                          vrf = 'management',
                          timeout = 9)
        expected_output = self.md.mock_data['serv_prompt']['commands']\
                              ['10.1.0.207']['response']
        test_output = '\n'.join(test_output.splitlines())
        expected_output = '\n'.join(expected_output.splitlines())
        self.assertIn(expected_output, test_output)

    def test_server_parameter(self):
        with self.assertRaisesRegex(SubCommandFailure,
                           'Server address must be specified for remote copy'):
            self.d.copy(source='tftp:', source_file='/tftpboot/mdear/n7k.gbin',
                            dest='bootflash:', vrf='management')
        expected_output = self.md.mock_data['dest_file']['commands']\
                              ['/cat3k_caa-universalk9.bld_polaris.bin']['response']
        test_output = self.d.copy(source='tftp://10.1.0.207/some.cfg', dest='bootflash:',
                       dest_file="/cat3k_caa-universalk9.bld_polaris.bin")
        test_output = '\n'.join(test_output.splitlines())
        expected_output = '\n'.join(expected_output.splitlines())
        self.assertIn(expected_output, test_output)

    def test_copy_tftp_sending_interrupt(self):
        self.d.copy.interrupt = 'send interrupt\n'
        with self.assertRaises(SubCommandFailure) as err:
            self.d.copy(source='tftp:',
                        dest='bootflash:',
                        source_file='/tftpboot/mdear/n7k.gbin',
                        server='10.1.0.207',
                        user='rcpuser',
                        password='123rcp!',
                        vrf='vrf_test1',
                        timeout=10)
        self.assertEqual(self.d.spawn.last_sent, 'send interrupt\n')
        self.assertIsInstance(err.exception.__cause__, TimeoutError)

    def test_copy_error_no_file(self):
        with self.assertRaises(SubCommandFailure) as err:
            self.d.copy(source='flash:',
                        dest='flash-3:',
                        source_file='/cat3k_caa-bld_xyz.bin',
                        dest_file='/cat3k_caa-bld_xyz.bin',
                        timeout=9)
        self.assertEqual(err.exception.args[0], 'Copy failed')


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosxrCopyService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxr --state enable'],
                           os='iosxr')
        cls.d.connect()
        cls.md = mock_device.MockDevice(device_os='iosxr', state='enable')

    @classmethod
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_wildcard_copy(self):
        output = self.d.copy(
            source='harddisk:',
            source_file='*.txt',
            dest='tftp:',
            dest_directory='auto/tftp/user/log_tmp',
            server='1.1.1.1',
        )
        output = '\n'.join(output.splitlines())
        file_confirms = ['copy_harddisk_wildcard_tftp_dest_confirm_1',
                         'copy_harddisk_wildcard_tftp_dest_confirm_2',
                         'copy_harddisk_wildcard_tftp_dest_confirm_3']
        for confirm in file_confirms:
            self.assertIn(
                self.md.mock_data[confirm]['commands']['']['response'], output)


class TestNxosCopyService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = Connection(hostname='Router',
                        start=['mock_device_cli --os nxos --state exec'],
                        os='nxos')
        cls.d.connect()
        cls.md = mock_device.MockDevice(device_os='nxos', state='exec')

    @classmethod
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_dest_file_parameter(self):
        test_output = self.d.copy(source='bootflash:', dest='scp:', dest_file='tmp/test.cfg',
                           server="10.0.0.7", source_file='run-cfg.cfg', vrf='management',
                           user='scpuser', password='scppwd')
        test_output = '\n'.join(test_output.splitlines())
        expected_output = self.md.mock_data['enter_pass']['commands']\
                              ['scppwd']['response']
        expected_output = '\n'.join(expected_output.splitlines())
        self.assertIn(expected_output, test_output)
        test_output = self.d.copy(source='bootflash:', dest='bootflash:',
                           source_file='test-1.cfg', dest_file="test-2.cfg")
        test_output = '\n'.join(test_output.splitlines())
        expected_output = self.md.mock_data['src_file']['commands']\
                              ['test-1.cfg']['response']
        expected_output = '\n'.join(expected_output.splitlines())
        self.assertIn(expected_output, test_output)

    def test_dns_failure(self):
        with self.assertRaisesRegex(SubCommandFailure, "Copy error message"):
            self.d.copy(source='scp:', dest='bootflash:',
                        server='unknownserver', source_file='/N9K/nxosgolden.bin',
                        vrf='dnsvrf', user='dnsuser', password='dnspwd')


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXeCopyService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxe --state enable_isr'],
                           os='iosxe')
        cls.d.connect()
        cls.md = mock_device.MockDevice(device_os='iosxe', state='enable_isr')

    @classmethod
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_to_tftp(self):
        output = self.d.copy(
            source='tftp:',
            dest='bootflash:',
            source_file='test',
            dest_file='test2',
            server='10.1.6.243',
            vrf='Mgmt-intf',
        )
        output = '\n'.join(output.splitlines())
        expected_output = \
            self.md.mock_data['copy_to_tftp_dest_filename_overwrite']\
            ['commands']['y']['response']
        expected_output = '\n'.join(expected_output.splitlines())
        self.assertIn(expected_output, output)

    def test_from_tftp(self):
        output = self.d.copy(
            source='bootflash:',
            dest='tftp:',
            source_file='test2',
            dest_file='test',
            server='10.1.6.243',
            vrf='Mgmt-intf',
        )
        output = '\n'.join(output.splitlines())
        expected_output = \
            self.md.mock_data['copy_from_tftp_dest_filename']\
            ['commands']['test']['response']
        expected_output = '\n'.join(expected_output.splitlines())
        self.assertIn(expected_output, output)



class TestMaxAttempts(unittest.TestCase):
    def setUp(self):
        self.md = MockDeviceTcpWrapperIOS(port=0, state='enable')
        self.md.mockdevice = NetworkCopyFailMockDevice(state='enable')
        self.md.start()
        self.dev = Connection(hostname='Router',
                     start=['telnet 127.0.0.1 {}'.format(self.md.ports[0])],
                     os='ios')
        self.dev.connect()

    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
    def tearDown(self):
        self.md.stop()
        self.dev.disconnect()

    def test_raise_bad_nw_exception(self):
        with self.assertRaisesRegex(SubCommandFailure, 'CopyBadNetworkError'):
            self.dev.copy(source='tftp:', source_file='/tftpboot/mdear/n7k.gbin',
                       dest='bootflash:', vrf='management', server='10.1.0.207')

    def test_max_attempt(self):
        self.dev.copy(source='tftp:', source_file='/tftpboot/mdear/n7k.gbin',
            dest='bootflash:', vrf='management', server='10.1.0.207', max_attempts=3)

if __name__ == '__main__':
    unittest.main()
