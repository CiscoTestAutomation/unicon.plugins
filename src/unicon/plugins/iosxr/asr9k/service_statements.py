__author__ = "Takashi Higashimura <tahigash@cisco.com>"

from unicon.eal.dialogs import Statement

from unicon.plugins.generic.service_statements import (save_env,
    confirm_reset, reload_confirm,
    reload_confirm_ios, useracess,
    confirm_config, setup_dialog,
    auto_install_dialog, module_reload,
    save_module_cfg, reboot_confirm,
    secure_passwd_std, admin_password,
    auto_provision, login_stmt,
    send_response, password_handler)
from unicon.plugins.iosxr.service_statements import confirm_module_reload_stmt

from .service_patterns import IOSXRASR9KReloadPatterns


pat = IOSXRASR9KReloadPatterns()


press_enter = Statement(pattern=pat.press_enter,
                                  action=send_response, args={'response': ''},
                                  loop_continue=True,
                                  continue_timer=False)

config_completed = Statement(pattern=pat.system_config_completed,
                                  action=send_response, args={'response': ''},
                                  loop_continue=False,
                                  continue_timer=False)

password_stmt = Statement(pattern=pat.password,
                          action=password_handler,
                          args=None,
                          loop_continue=True,
                          continue_timer=False)

reloading_node_stmt = Statement(pattern=pat.reloading_node,
                                action=None,
                                args=None,
                                loop_continue=False,
                                continue_timer=False)


reload_statement_list = [save_env,
                         confirm_reset,
                         reload_confirm,
                         reload_confirm_ios,
                         useracess,
                         confirm_config,
                         setup_dialog,
                         auto_install_dialog,
                         module_reload,
                         save_module_cfg,
                         reboot_confirm,
                         secure_passwd_std,
                         admin_password,
                         auto_provision,
                         login_stmt,
                         password_stmt,
                         press_enter,
                         confirm_module_reload_stmt,
                         config_completed, # loop_continue=False
                        ]

reload_statement_list_vty = [reload_confirm,
                             reload_confirm_ios,
                             reloading_node_stmt # loop_continue=False
                            ]
