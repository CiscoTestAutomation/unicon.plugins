"""
Unittests for NXOS/N9K plugin
Uses the unicon.plugins.tests.mock.mock_device_nxos for test.
"""
__author__ = 'Difu Hu <difhu@cisco.com>'

import re
import unittest
from unittest.mock import Mock, patch

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.statements import generic_statements
from unicon.plugins.nxos.n9k import Nxos9kDualRPConnection
from unicon.plugins.nxos.n9k.connection_provider import (
    Nxos9kDualRpConnectionProvider)
from unicon.plugins.nxos.n9k.service_implementation import (
    Nxos9kReload, HANxos9kReloadService)
from unicon.plugins.nxos.n9k.service_statements import (
    admin_password_setup_stmt, secure_password_setup_stmt,
    setup_syslog_stmt)
from unicon.plugins.nxos.service_implementation import (
    Reload, HANxosReloadService)
from unicon.plugins.nxos.service_statements import (
    admin_password, secure_password)


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestNxos9kPluginReloadService(unittest.TestCase):

    def test_secure_password_prompt_before_boot_syslog(self):
        dev = Connection(
            hostname='gamut',
            start=['mock_device_cli --os nxos --state exec'],
            os='nxos',
            platform='n9k',
        )
        dialog = dev.connection_provider_class(dev).get_connection_dialog()
        prompt = ("Do you want to enforce secure password standard "
                  "(yes/no) [y]: ")
        syslog = ("2026 Sep 24 15:21:54  %$ VDC-1 %$ "
                  "%VDC_MGR-2-VDC_ONLINE: vdc 1 has come online\r\n")

        self.assertRegex(prompt + syslog,
                         generic_statements.syslog_msg_stmt.pattern)
        syslog_match = next(stmt for stmt in dialog
                            if re.search(stmt.pattern, syslog, re.S))
        self.assertIs(syslog_match.action,
                      setup_syslog_stmt.action)
        for output in (prompt + syslog,
                       syslog + prompt + '  Enter the password for "admin": '):
            first_match = next(stmt for stmt in dialog
                               if re.search(stmt.pattern, output, re.S))
            self.assertEqual(first_match.pattern, secure_password.pattern)
            self.assertEqual(first_match.args['response'], 'n')

    def test_reload_dialog_prioritizes_secure_password(self):
        dev = Connection(
            hostname='gamut',
            start=['mock_device_cli --os nxos --state exec'],
            os='nxos',
            platform='n9k',
        )
        service = Nxos9kReload(dev, dev.context)
        with patch.object(Reload, 'call_service') as parent:
            service.call_service()
        dialog = service.service_dialog(
            service_dialog=parent.call_args.kwargs['dialog'])
        dialog += service.dialog
        output = ('2026 Sep 25 02:14:49  %$ VDC-1 %$ '
                  '%VDC_MGR-2-VDC_ONLINE: vdc 1 has come online\r\n'
                  'Do you want to enforce secure password standard '
                  '(yes/no) [y]: \r\n'
                  '  Enter the password for "admin": ')
        first_match = next(stmt for stmt in dialog
                           if re.search(stmt.pattern, output, re.S))
        self.assertEqual(first_match.pattern, secure_password.pattern)
        self.assertEqual(first_match.args['response'], 'n')
        syslog = output.split('Do you want', 1)[0]
        syslog_match = next(stmt for stmt in dialog
                            if re.search(stmt.pattern, syslog, re.S))
        self.assertIs(syslog_match.action,
                      setup_syslog_stmt.action)
        for prompt in ('Enter', 'Confirm'):
            output = f'{prompt} the password for "admin": '
            first_match = next(stmt for stmt in dialog
                               if re.search(stmt.pattern, output, re.S))
            self.assertEqual(first_match.pattern, admin_password.pattern)
            self.assertIs(first_match.action, admin_password_setup_stmt.action)

    def test_ha_reload_preserves_secure_password_priority(self):
        service = object.__new__(HANxos9kReloadService)
        service.context = {}
        with patch.object(HANxosReloadService, 'call_service') as parent:
            service.call_service()
        dialog = parent.call_args.kwargs['dialog']
        output = ('Do you want to enforce secure password standard '
                  '(yes/no) [y]: \r\n'
                  '  Enter the password for "admin": ')
        first_match = next(stmt for stmt in dialog
                           if re.search(stmt.pattern, output, re.S))
        self.assertEqual(first_match.pattern, secure_password.pattern)
        for prompt in ('Enter', 'Confirm'):
            output = f'{prompt} the password for "admin": '
            first_match = next(stmt for stmt in dialog
                               if re.search(stmt.pattern, output, re.S))
            self.assertEqual(first_match.pattern, admin_password.pattern)

    def test_admin_setup_password_precedes_generic_login_password(self):
        dev = Connection(
            hostname='gamut',
            start=['mock_device_cli --os nxos --state exec'],
            os='nxos',
            platform='n9k',
        )
        dialog = dev.connection_provider_class(dev).get_connection_dialog()
        for prompt in ('Enter', 'Confirm'):
            output = f'{prompt} the password for "admin": '
            first_match = next(stmt for stmt in dialog
                               if re.search(stmt.pattern, output, re.S))
            self.assertEqual(first_match.pattern, admin_password.pattern)
            self.assertIs(first_match.action, admin_password_setup_stmt.action)

    def test_syslog_recovers_prompt_outside_password_setup(self):
        dev = Connection(
            hostname='gamut',
            start=['mock_device_cli --os nxos --state exec'],
            os='nxos', platform='n9k')
        connection_dialog = (
            dev.connection_provider_class(dev).get_connection_dialog())
        service = Nxos9kReload(dev, dev.context)
        with patch.object(Reload, 'call_service') as parent:
            service.call_service()
        reload_dialog = service.service_dialog(
            service_dialog=parent.call_args.kwargs['dialog'])
        reload_dialog += service.dialog
        ha_service = object.__new__(HANxos9kReloadService)
        ha_service.context = {}
        with patch.object(HANxosReloadService, 'call_service') as parent:
            ha_service.call_service()
        ha_dialog = parent.call_args.kwargs['dialog']

        syslog = ('2026 Sep 25 02:14:49  %$ VDC-1 %$ '
                  '%VDC_MGR-2-VDC_ONLINE: vdc 1 has come online\r\n')
        for dialog in (connection_dialog, reload_dialog, ha_dialog):
            with self.subTest(dialog=dialog):
                statement = next(
                    stmt for stmt in dialog
                    if re.search(stmt.pattern, syslog, re.S))
                self.assertIs(statement.action, setup_syslog_stmt.action)
                spawn = Mock()
                spawn.buffer = syslog
                spawn.settings.SYSLOG_WAIT = 0
                spawn.settings.BOOT_SETUP_SYSLOG_WAIT = 0
                session = {'buffer_len': len(syslog)}

                statement.action(spawn, session)
                spawn.sendline.assert_called_once_with()
                spawn.sendline.reset_mock()

                with patch.object(secure_password, 'action') as send_no:
                    secure_password_setup_stmt.action(spawn, session, 'n')
                send_no.assert_called_once_with(spawn, response='n')
                statement.action(spawn, session)
                spawn.sendline.assert_not_called()
                self.assertEqual(spawn.buffer, '')

                with patch.object(admin_password, 'action') as send_pass:
                    spawn.match.last_match.group.return_value = 'Enter'
                    admin_password_setup_stmt.action(spawn, {}, session)
                    spawn.match.last_match.group.return_value = 'Confirm'
                    admin_password_setup_stmt.action(spawn, {}, session)
                self.assertEqual(send_pass.call_count, 2)
                self.assertNotIn('n9k_password_setup_pending', session)

                spawn.buffer = syslog
                statement.action(spawn, session)
                spawn.sendline.assert_called_once_with()

    def test_boot_syslog_waits_for_secure_password_prompt(self):
        syslog = ('2026 Sep 25 02:14:49  %$ VDC-1 %$ '
                  '%VDC_MGR-2-VDC_ONLINE: vdc 1 has come online\r\n')
        prompt = ('Do you want to enforce secure password standard '
                  '(yes/no) [y]: ')
        spawn = Mock()
        spawn.buffer = syslog
        spawn.settings.SYSLOG_WAIT = 0
        spawn.settings.BOOT_SETUP_SYSLOG_WAIT = 30
        session = {'buffer_len': len(syslog)}

        def receive_prompt():
            spawn.buffer += prompt
            return True

        spawn.read_update_buffer.side_effect = receive_prompt
        setup_syslog_stmt.action(spawn, session)

        spawn.sendline.assert_not_called()
        self.assertIn(prompt, spawn.buffer)

    def test_secure_password_respects_connect_reply(self):
        custom = Statement(pattern=secure_password.pattern,
                           action='sendline(yes)', loop_continue=True)
        admin_custom = Statement(pattern=admin_password.pattern,
                                 action='sendline(custom)', loop_continue=True)
        dev = Connection(
            hostname='gamut',
            start=['mock_device_cli --os nxos --state exec'],
            os='nxos',
            platform='n9k',
            connect_reply=Dialog([custom, admin_custom]),
        )
        dialog = dev.connection_provider_class(dev).get_connection_dialog()
        first_match = next(stmt for stmt in dialog if re.search(
            stmt.pattern,
            'Do you want to enforce secure password standard (yes/no) [y]: ',
            re.S))
        self.assertIs(first_match.action, custom.action)
        first_admin_match = next(stmt for stmt in dialog if re.search(
            stmt.pattern, 'Confirm the password for "admin": ', re.S))
        self.assertIs(first_admin_match.action, admin_custom.action)

    def test_other_nxos_platforms_keep_their_dialog_order(self):
        dev = Connection(hostname='switch',
                         start=['mock_device_cli --os nxos --state exec'],
                         os='nxos')
        patterns = [stmt.pattern for stmt in
                    dev.connection_provider_class(dev).get_connection_dialog()]
        self.assertLess(
            patterns.index(generic_statements.syslog_msg_stmt.pattern),
            patterns.index(secure_password.pattern))
        generic_dialog = (
            dev.connection_provider_class(dev).get_connection_dialog())
        generic_syslog = next(
            stmt for stmt in generic_dialog
            if stmt.pattern == generic_statements.syslog_msg_stmt.pattern)
        self.assertIs(generic_syslog.action,
                      generic_statements.syslog_msg_stmt.action)
        self.assertIs(Nxos9kDualRPConnection.connection_provider_class,
                      Nxos9kDualRpConnectionProvider)

    @classmethod
    def setUpClass(cls):
        cls.dev = Connection(
            hostname='N93_1',
            start=['mock_device_cli --os nxos --state login3 --hostname N93_1'],
            os='nxos',
            platform='n9k',
            username='cisco',
            tacacs_password='cisco',
            enable_password='cisco'
        )

    def test_reload_boot_image_succeed(self):
        self.dev.connect()
        self.dev.reload(image_to_boot='ISSUCleanGolden.system.gbin')
        self.dev.disconnect()

    def test_reload_without_boot_image_fail(self):
        self.dev.connect()
        with self.assertRaises(SubCommandFailure):
            self.dev.reload()
        self.dev.disconnect()

    def test_reload_with_wrong_boot_image_fail(self):
        self.dev.connect()
        with self.assertRaises(SubCommandFailure):
            self.dev.reload(image_to_boot='WrongImage.system.gbin')
        self.dev.disconnect()

class TestNxosN9KAttachConsole(unittest.TestCase):

    def test_attach_console(self):
        c = Connection(hostname='LEAF',
                       start=['mock_device_cli --os nxos --state n9k_connect2'],
                       os='nxos',
                       platform='n9k',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco'
        )
        c.connect()
        with c.attach_console(module_num=1) as mod:
            mod.execute('show version')
        c.disconnect()

if __name__ == "__main__":
    unittest.main()
