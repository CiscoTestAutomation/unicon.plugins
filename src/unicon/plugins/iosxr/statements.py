__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.plugins.generic.statements import GenericStatements, more_prompt_handler
from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.helpers import sendline
from unicon.core.errors import SubCommandFailure, SwitchoverDisallowedError

from unicon.plugins.utils import (
    get_current_credential,
    common_cred_username_handler,
    common_cred_password_handler,
)

patterns = IOSXRPatterns()


def handle_commit_changes(spawn, context):
    """Handle pending changes while leaving configuration mode.

    During initial connection, discard pending changes so an inconsistent SDR
    can reach exec mode without attempting a commit. Preserve the existing
    commit behavior for normal state transitions after connection.
    """
    if context.get('_iosxr_initial_connection'):
        context['_iosxr_uncommitted_changes'] = True
        spawn.sendline('no')
    else:
        spawn.sendline('yes')


def handle_failed_config(spawn, abort=True):
    spawn.read_update_buffer()
    spawn.sendline("show configuration failed")
    if abort:
        spawn.expect([patterns.config_prompt])
        spawn.sendline("abort")


def recover_config_transaction_lock(spawn, context, state_machine, start_state, end_state, initial_output):
    timeout = context.get('config_transaction_lock_timeout')
    context['config_transaction_lock_output'] = initial_output
    try:
        try:
            spawn.sendline('show configuration commit changes last 1')
            config_state = state_machine.get_state(start_state)
            result = spawn.expect([config_state.pattern], timeout=timeout)
            context['config_transaction_lock_output'] += result.match_output
        finally:
            spawn.sendline('abort')
            if start_state == 'admin_conf':
                admin_state = state_machine.get_state('admin')
                spawn.expect([admin_state.pattern], timeout=timeout)
                spawn.sendline('exit')
            end_state_pattern = state_machine.get_state(end_state).pattern
            spawn.expect([end_state_pattern], timeout=timeout)
    except Exception as err:
        raise SubCommandFailure(
            'Configuration transaction lock recovery failed:\n{}'
            .format(context['config_transaction_lock_output']), err) from err
    context['config_transaction_locked'] = True


def switchover_disallowed_handler(error):
    raise SwitchoverDisallowedError(error)


def password_handler(spawn, context, session):
    """handles password prompt"""
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(
            spawn=spawn,
            context=context,
            credential=credential,
            session=session,
            reuse_current_credential=True,
        )
    else:
        spawn.sendline(context["tacacs_password"])


class IOSXRStatements(GenericStatements):

    def __init__(self):
        super().__init__()
        self.secret_password_stmt = Statement(
            pattern=patterns.secret_password_prompt,
            action=password_handler,
            args=None,
            loop_continue=True,
            continue_timer=False,
        )
        self.commit_replace_stmt = Statement(
            pattern=patterns.commit_replace_prompt,
            action=sendline,
            args={"command": "yes"},
            loop_continue=True,
            continue_timer=False,
        )
        self.confirm_y_prompt_stmt = Statement(
            pattern=patterns.confirm_y_prompt,
            action=sendline,
            args={"command": "y"},
            loop_continue=True,
            continue_timer=False,
        )
        self.more_prompt_stmt = Statement(
            pattern=patterns.more_prompt,
            action=more_prompt_handler,
            args=None,
            loop_continue=True,
            continue_timer=False,
            trim_buffer=False,
        )


iosxr_statements = IOSXRStatements()

authentication_statement_list = [
    iosxr_statements.bad_password_stmt,
    iosxr_statements.login_incorrect,
    iosxr_statements.login_stmt,
    iosxr_statements.useraccess_stmt,
    iosxr_statements.password_stmt,
    iosxr_statements.secret_password_stmt,
]
