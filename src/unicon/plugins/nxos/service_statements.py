"""
Module:
    unicon.plugins.service.nxos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining all Services Statement, handlers(callback) and Statement
    list for service dialog would be defined here.
"""
from time import sleep

from unicon.eal.dialogs import Statement
from unicon.plugins.nxos.patterns import NxosPatterns
from unicon.plugins.nxos.service_patterns import ReloadPatterns
from unicon.plugins.nxos.service_patterns import HaNxosReloadPatterns

from unicon.plugins.generic.service_statements import send_response,\
    login_handler, password_handler, connection_closed_stmt
from unicon.plugins.generic.service_statements import save_env,\
    reload_proceed, auto_install_dialog, \
    setup_dialog, config_byte, login_notready, redundant, confirm_reset,\
    press_enter, confirm_config, module_reload, save_module_cfg,\
    secure_passwd_std

from unicon.plugins.utils import (get_current_credential,
    common_cred_username_handler, common_cred_password_handler, )


def run_level():
    sleep(100)


def nxos_system_up():
    sleep(100)


def admin_password_handler(spawn, context, session):
    """ handles admin password prompt
    """
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(
            spawn=spawn, context=context, credential=credential,
            session=session, reuse_current_credential=True)
    else:
        spawn.sendline(context['tacacs_password'])


# Additional statement specific to nxos
pat = HaNxosReloadPatterns()

reboot = Statement(pattern=pat.reboot,
                   action=send_response,
                   args={'response': 'y'},
                   loop_continue=True,
                   continue_timer=True)

secure_password = Statement(pattern=pat.secure_password,
                            action=send_response,
                            args={'response': 'n'},
                            loop_continue=True,
                            continue_timer=True)

admin_password = Statement(pattern=pat.admin_password,
                           action=admin_password_handler,
                           args=None,
                           loop_continue=True,
                           continue_timer=False)

enable_vdc = Statement(pattern=pat.enable_vdc,
                       action=send_response,
                       args={'response': 'no'},
                       loop_continue=True,
                       continue_timer=True)

snmp_port = Statement(pattern=pat.snmp_port,
                      action=send_response,
                      args={'response': ''},
                      loop_continue=True,
                      continue_timer=True)

boot_vdc = Statement(pattern=pat.boot_vdc,
                     action=send_response,
                     args={'response': 'yes'},
                     loop_continue=True,
                     continue_timer=True)

login_stmt = Statement(pattern=pat.username,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=False)

password_stmt = Statement(pattern=pat.password,
                          action=password_handler,
                          args=None,
                          loop_continue=False,
                          continue_timer=False)

useracess1 = Statement(pattern=pat.useracess,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=False)

run_init = Statement(pattern=pat.run_init,
                     action=run_level,
                     args=None,
                     loop_continue=True,
                     continue_timer=False)

system_up = Statement(pattern=pat.system_up,
                      action=nxos_system_up,
                      args=None,
                      loop_continue=True,
                      continue_timer=False)

skip_poap = Statement(pattern=pat.skip_poap,
                      action=send_response,
                      args={'response': 'yes'},
                      loop_continue=True,
                      continue_timer=True)

# TODO finalise on this step
loader_prompt = None
rommon_prompt = None

# for nxos single rp reload
pat = ReloadPatterns()
reload_confirm_nxos = Statement(pattern=pat.reload_confirm_nxos,
                                action=send_response,
                                args={'response': 'y'},
                                loop_continue=True,
                                continue_timer=False)

auto_provision_nxos = Statement(pattern=pat.auto_provision_nxos,
                                action=send_response,
                                args={'response': 'y'},
                                loop_continue=True,
                                continue_timer=False)

# reload statement list for nxos single-rp

nxos_reload_statement_list = [save_env, confirm_reset, reload_confirm_nxos,
                              press_enter, login_stmt, password_stmt,
                              confirm_config, setup_dialog,
                              auto_install_dialog, module_reload,
                              save_module_cfg, secure_passwd_std,
                              admin_password, auto_provision_nxos, enable_vdc,
                              skip_poap, connection_closed_stmt]

# reload statement list for nxos dual-rp
ha_nxos_reload_statement_list = [save_env, reboot, secure_password,
                                 auto_provision_nxos, reload_proceed,
                                 auto_install_dialog, admin_password,
                                 setup_dialog, config_byte, enable_vdc,
                                 snmp_port, boot_vdc, login_notready,
                                 redundant, login_stmt, password_stmt,
                                 system_up, run_init, useracess1,
                                 skip_poap]

additional_connection_dialog = [enable_vdc, boot_vdc, snmp_port,
                                admin_password, secure_password, auto_provision_nxos]

# Statements for commit verification on NXOS
pat = NxosPatterns()

commit_verification_stmt = Statement(pattern=pat.commit_verification,
                                     action='sendline()',
                                     args=None, loop_continue=True,
                                     continue_timer=False)

config_commit_stmt_list = [commit_verification_stmt]

# Statements for execute service on NXOS
pat = NxosPatterns()


nxos_module_reload_stmt = Statement(pattern=pat.nxos_module_reload,
                                    action='sendline(y)',
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=False)

execute_stmt_list = [nxos_module_reload_stmt]
