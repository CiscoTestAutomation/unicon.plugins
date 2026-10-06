__author__ = "Syed Raza <syedraza@cisco.com>"

import re
import time

from random import randint

from unicon.eal.dialogs import Dialog
from unicon.statemachine import State

from unicon.core.errors import StateMachineError, TimeoutError
from unicon.bases.routers.connection_provider \
    import BaseSingleRpConnectionProvider, BaseDualRpConnectionProvider

from unicon.plugins.generic.statements import custom_auth_statements
from unicon.plugins.generic.statements import pre_connection_statement_list
from unicon.plugins.generic.patterns import GenericPatterns


from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.plugins.iosxr.errors import RpNotRunningError
from unicon.plugins.iosxr.statements import authentication_statement_list


patterns = IOSXRPatterns()


_INITIAL_CONNECTION = '_iosxr_initial_connection'
_UNCOMMITTED_CHANGES = '_iosxr_uncommitted_changes'
_RECOVERY_CONTEXT_KEYS = (
    _INITIAL_CONNECTION,
    _UNCOMMITTED_CHANGES,
)


def _recover_configuration_inconsistency(con, prompt_recovery=False):
    """Detect and clear an IOS XR SDR configuration inconsistency."""
    context = con.context
    if not context.pop(_UNCOMMITTED_CHANGES, False):
        return

    # Answering "no" gets us safely to exec mode, but it also suppresses the
    # blocked-commit warning. Re-enter config without staging changes so XR
    # reports whether this is the SDR inconsistency case.
    con.log.info('Probing IOS XR configuration state after discarding '
                 'uncommitted changes')
    state_machine = con.state_machine
    try:
        probe_output = state_machine.go_to(
            'config',
            con.spawn,
            context=context,
            prompt_recovery=prompt_recovery,
            timeout=con.settings.CONFIG_TIMEOUT,
        )
    except StateMachineError:
        # Essential-ops mode cannot enter config, so the transition correctly
        # fails. Classify that known response without hiding other transition
        # failures such as an exhausted configuration-lock retry.
        probe_output = (con.spawn.match.match_output
                        if con.spawn.match else '')
        if re.search(
                patterns.essential_ops_message,
                probe_output,
                re.MULTILINE):
            con.log.warning('IOS XR is in essential-ops mode; skipping SDR '
                            'configuration inconsistency recovery')
            return
        raise

    # The warning is informational rather than a prompt/state, so classify it
    # from the complete state-transition output.
    config_inconsistent = re.search(
        patterns.configuration_inconsistency_message,
        probe_output,
        re.MULTILINE,
    )

    # The recovery command is exec-only, so unwind the probe before acting on
    # its result.
    if state_machine.current_state == 'config':
        con.enable()

    if not config_inconsistent:
        return

    con.log.warning('IOS XR SDR running configuration is inconsistent with '
                    'persistent configuration; clearing the inconsistency')
    con.execute(
        con.settings.CLEAR_CONFIG_INCONSISTENCY_CMD,
        prompt_recovery=prompt_recovery,
    )


class IOSXRSingleRpConnectionProvider(BaseSingleRpConnectionProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def establish_connection(self, connection_dialog=None,
                             skip_initialization=False):
        """Detect and normalize the initial IOS XR state.

        Args:
            connection_dialog (Dialog, optional): Replacement dialog for
                initial state detection. When omitted, the normal provider
                dialog is used.
            skip_initialization (bool): Stop after initial state detection.
        """
        con = self.connection
        context = con.context
        # Limit the discard behavior to the transition that normalizes the
        # device's initial state. Initialization and later user transitions
        # must retain the established commit-prompt behavior.
        context[_INITIAL_CONNECTION] = True
        try:
            establish_kwargs = {}
            if connection_dialog is not None:
                establish_kwargs['connection_dialog'] = connection_dialog
            if skip_initialization:
                establish_kwargs['skip_initialization'] = True
            output = super().establish_connection(**establish_kwargs)
            if skip_initialization:
                return output
            # The IOS XR exclusive prompt overlaps the general config prompt
            # and may be selected during initial state detection.
            if con.state_machine.current_state == 'exclusive':
                con.enable()
            _recover_configuration_inconsistency(
                con,
                prompt_recovery=self.prompt_recovery,
            )
            return output
        finally:
            for key in _RECOVERY_CONTEXT_KEYS:
                context.pop(key, None)

    def set_init_commands(self):
        con = self.connection

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            self.init_exec_commands = con.settings.IOSXR_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            self.init_config_commands = con.settings.IOSXR_INIT_CONFIG_COMMANDS

    def get_connection_dialog(self):
        con = self.connection
        connection_statement_list = authentication_statement_list + \
            pre_connection_statement_list
        custom_auth_stmt = custom_auth_statements(
                             self.connection.settings.LOGIN_PROMPT,
                             self.connection.settings.PASSWORD_PROMPT)
        if custom_auth_stmt:
            connection_statement_list = custom_auth_stmt + connection_statement_list
        return con.connect_reply + Dialog(connection_statement_list)


class IOSXRDualRpConnectionProvider(BaseDualRpConnectionProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_init_commands(self):
        con = self.connection

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            self.init_exec_commands = con.settings.IOSXR_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            self.init_config_commands = con.settings.IOSXR_INIT_CONFIG_COMMANDS

    def get_connection_dialog(self):
        con = self.connection
        connection_statement_list = authentication_statement_list + \
            pre_connection_statement_list
        custom_auth_stmt = custom_auth_statements(
                             self.connection.settings.LOGIN_PROMPT,
                             self.connection.settings.PASSWORD_PROMPT)
        if custom_auth_stmt:
            connection_statement_list = custom_auth_stmt + connection_statement_list
        return con.connect_reply + Dialog(connection_statement_list)

    def designate_handles(self):
        """ Identifies the Role of each handle and designates if it is active or
            standby and bring the active RP to enable state """
        con = self.connection
        subcons = list(con._subconnections.items())
        subcon1_alias, subcon1 = subcons[0]
        subcon2_alias, subcon2 = subcons[1]
        if subcon1.state_machine.current_state == 'standby_locked':
            target_con = subcon2
            other_con = subcon1
            target_alias = subcon2_alias
            other_alias = subcon1_alias
        elif subcon2.state_machine.current_state == 'standby_locked':
            target_con = subcon1
            other_con = subcon2
            target_alias = subcon1_alias
            other_alias = subcon2_alias
        else:
            con.log.info("None of the RPs are currently in standby locked state")
            target_con = subcon2
            other_con = subcon1
            target_alias = subcon2_alias
            other_alias = subcon1_alias

        con._set_active_alias(target_alias)
        con._set_standby_alias(other_alias)
        context = target_con.context
        context[_INITIAL_CONNECTION] = True
        try:
            target_con.state_machine.go_to(
                'enable',
                target_con.spawn,
                context=context,
                timeout=target_con.connection_timeout,
                dialog=self.get_connection_dialog(),
            )
            _recover_configuration_inconsistency(
                target_con,
                prompt_recovery=self.prompt_recovery,
            )
        finally:
            for key in _RECOVERY_CONTEXT_KEYS:
                context.pop(key, None)
        con._handles_designated = True

    def connect(self, connection_dialog=None, skip_initialization=False):
        """Connect, initialize, and designate the IOS XR handles.

        Args:
            connection_dialog (Dialog, optional): Replacement dialog for
                initial state detection. When omitted, the normal provider
                dialog is used.
            skip_initialization (bool): Stop after initial state detection.
        """
        con = self.connection

        establish_kwargs = {}
        if connection_dialog is not None:
            establish_kwargs['connection_dialog'] = connection_dialog
        if skip_initialization:
            establish_kwargs['skip_initialization'] = True
            return self.establish_connection(**establish_kwargs)

        for subconnection in con.subconnections:
            con.log.info('+++ connection to %s +++' % str(subconnection.spawn))
        if con.learn_tokens or con.settings.LEARN_DEVICE_TOKENS:
            # Add learn tokens state to state machine so it can use a looser
            # prompt pattern to match. Required for at least some Linux prompts
            for subconnection in con.subconnections:
                if 'learn_tokens_state' not in \
                        [str(s) for s in subconnection.state_machine.states]:
                    self.learn_tokens_state = State('learn_tokens_state',
                                            GenericPatterns().learn_os_prompt)
                    subconnection.state_machine.add_state(self.learn_tokens_state)
        self.establish_connection(**establish_kwargs)
        # Maintain initial state
        if not con.mit:
            con.log.info('+++ designating handles +++')
            self.designate_handles()

            # Run initial exec/configure commands on the active, which is
            # supposed to disable console logging.
            con.log.info('+++ initializing active handle +++')
            self.init_active()


class IOSXRVirtualConnectionProviderLaunchWaiter(object):
    """ This class is meant to be multiply inherited along with the
    appropriate connection provider base class.
    """

    def wait_for_launch_complete(self,
            initial_discovery_wait_sec, initial_wait_sec, post_prompt_wait_sec,
            connection, log, hostname, checkpoint_pattern,
            learn_hostname=False):
        con = connection
        # Checking if a device is launching or not
        log.info('Trying to connect to prompt on device {} ...'.\
            format(hostname))
        spawn = connection.spawn

        initial_prompts = [
            patterns.enable_prompt.replace('%N',
                con.settings.DEFAULT_LEARNED_HOSTNAME if learn_hostname else hostname),
            patterns.config_prompt.replace('%N',
                con.settings.DEFAULT_LEARNED_HOSTNAME if learn_hostname else hostname),
            patterns.secret_password_prompt,
            patterns.username_prompt,
            patterns.password_prompt,
            patterns.standby_prompt,
            patterns.logout_prompt ]

        result = False
        dialog = Dialog([[p, None, None, False, False] for p in initial_prompts])
        for x in range(connection.settings.INITIAL_DISCOVERY_RETRIES):
            try:
                spawn.sendline()
                result = dialog.process(spawn, timeout=initial_discovery_wait_sec)
                if result:
                    break
            except TimeoutError:
                pass

        if result is False:
            log.info("Can not access prompt on device {} so assuming "
                " virtual launch is in progress ...".\
                format(hostname))

            dialog += Dialog([[p, None, None, False, False] \
                for p in [checkpoint_pattern, patterns.standby_prompt]])

            result = dialog.process(spawn, timeout=initial_wait_sec)

            log.info("Final steps in launching virtual device {} detected: "
                "will attempt to access prompt in ~{} seconds.".\
                format(hostname, post_prompt_wait_sec))
            # Random timer to display prompts from different routers with a
            # slight delay from each other
            time.sleep(post_prompt_wait_sec - 10 + randint(10, 30))
