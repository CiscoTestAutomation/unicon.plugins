__author__ = "Syed Raza <syedraza@cisco.com>"

import time

from random import randint

from unicon.eal.dialogs import Dialog
from unicon.core.errors import TimeoutError
from unicon.bases.routers.connection_provider \
    import BaseSingleRpConnectionProvider, BaseDualRpConnectionProvider

from unicon.plugins.generic.statements import custom_auth_statements
from unicon.plugins.generic.statements import pre_connection_statement_list

from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.plugins.iosxr.errors import RpNotRunningError
from unicon.plugins.iosxr.statements import authentication_statement_list


patterns = IOSXRPatterns()


class IOSXRSingleRpConnectionProvider(BaseSingleRpConnectionProvider):

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
        target_con.state_machine.go_to('enable',
                                          target_con.spawn,
                                          context=target_con.context,
                                          timeout=target_con.connection_timeout,
                                          dialog=self.get_connection_dialog(),
                                          )
        con._handles_designated = True

    def connect(self):
        """ Connects, initializes and designates handle """
        con = self.connection

        for subconnection in con.subconnections:
            con.log.info('+++ connection to %s +++' % str(subconnection.spawn))
        self.establish_connection()

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

