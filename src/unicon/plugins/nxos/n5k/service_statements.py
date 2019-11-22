from unicon.eal.dialogs import Statement
from .service_patterns import NxosN5kReloadPatterns

from unicon.plugins.nxos.service_statements import (login_stmt, password_stmt,
    enable_vdc, admin_password)

from unicon.plugins.generic.service_statements import (save_env,
    auto_provision, auto_install_dialog,
    setup_dialog, confirm_reset,
    press_enter, confirm_config, module_reload, save_module_cfg,
    secure_passwd_std, )

# for nxos n5k single rp reload
pat = NxosN5kReloadPatterns()
reload_confirm_nxos = Statement(pattern=pat.reload_confirm_nxos,
                                action='sendline(y)',
                                loop_continue=True,
                                continue_timer=False)

# reload statement list for nxos n5k single-rp
nxos_reload_statement_list = [save_env, confirm_reset, reload_confirm_nxos,
                              press_enter, login_stmt, password_stmt,
                              confirm_config, setup_dialog,
                              auto_install_dialog, module_reload,
                              save_module_cfg, secure_passwd_std,
                              admin_password, auto_provision, enable_vdc]
