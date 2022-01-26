
import warnings


from time import sleep

from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog

from unicon.plugins.generic.statements import (
    custom_auth_statements,
    default_statement_list)

from unicon.plugins.generic.service_statements import ha_reload_statement_list
from unicon.plugins.generic.service_implementation import HAReloadService as BaseService

from unicon.plugins.generic.statements import connection_statement_list

from .service_statements import change_rp

from unicon.plugins.iosxe.service_implementation import \
     HAConfigure as XeConfigure, \
     HAExecute as XeExecute

class Configure(XeConfigure):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    def pre_service(self, *args, **kwargs):

        con=self.connection
        if 'target' in kwargs:
            if kwargs['target'] == 'standby':
                con.active.log.info('Could not execute any command on standby for this device')
                raise NotImplementedError
        super().pre_service(*args, **kwargs)

class Execute(XeExecute):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def pre_service(self, *args, **kwargs):
        con=self.connection
        if 'target' in kwargs:
            if kwargs['target'] == 'standby':
                con.active.log.info('could not execute any command on standby for the this device')
                raise NotImplementedError
        super().pre_service(*args, **kwargs)



class Reload(BaseService):
    """ Service to reload the device.

    Arguments:
        reload_command: reload command to be used. default "redundancy reload shelf"
        reload_creds: credential or list of credentials to use to respond to
                      username/password prompts.
        reply: Additional Dialog( i.e patterns) to be handled
        timeout: Timeout value in sec, Default Value is 60 sec
        return_output: if True, return namedtuple with result and reload output

    Returns:
        console True on Success, raises SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.reload()
            # If reload command is other than 'redundancy reload shelf'
            rtr.reload(reload_command="reload location all", timeout=700)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.dialog = Dialog(ha_reload_statement_list + default_statement_list + [change_rp])
        self.command = 'reload'
        self.__dict__.update(kwargs)

    def call_service(self,  # noqa: C901
                     reload_command=None,
                     dialog=Dialog([]),
                     reply=Dialog([]),
                     timeout=None,
                     reload_creds=None,
                     return_output=False,
                     *args,
                     **kwargs):
        con = self.connection
        if reply:
            if dialog:
                con.log.warning("**** Both 'reply' and 'dialog' were provided "
                                "to the reload service.  Ignoring 'dialog'.")
            dialog = reply
        elif dialog:
            warnings.warn('**** "dialog" parameter is deprecated.  '
                          'Use "reply" instead. ****',
                          category=DeprecationWarning)

        timeout = timeout or self.timeout

        command = reload_command or self.command

        fmt_str = "+++ reloading  %s  with reload_command %s and timeout is %s +++"
        con.log.info(fmt_str % (con.hostname, command, timeout))
        dialog += self.dialog
        custom_auth_stmt = custom_auth_statements(con.settings.LOGIN_PROMPT, con.settings.PASSWORD_PROMPT)

        if reload_creds:
            context = con.active.context.copy()
            context.update(cred_list=reload_creds)
            sby_context = con.standby.context.copy()
            sby_context.update(cred_list=reload_creds)
        else:
            context = con.active.context
            sby_context = con.standby.context

        if custom_auth_stmt:
            dialog += Dialog(custom_auth_stmt)

        # Issue reload command
        con.active.spawn.sendline(command)
        try:
            dialog.process(con.active.spawn,
                           context=context,
                           prompt_recovery=self.prompt_recovery,
                           timeout=timeout)
        except Exception as e:
            raise SubCommandFailure('Error during reload', e) from e
        else:
            con.active.state_machine._current_state= 'stby_locked'
        # Bring standby to good state.
        con.log.info('Waiting for config sync to finish')
        if con.standby.state_machine.current_state == 'stby_locked':
            con.standby.state_machine._current_state = 'generic'
        standby_wait_time = con.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT
        standby_wait_interval = 50
        standby_sync_try = standby_wait_time // standby_wait_interval + 1
        for round in range(standby_sync_try):
            con.standby.spawn.sendline()
            try:
                con.standby.state_machine.go_to(
                    'any',
                    con.standby.spawn,
                    context=sby_context,
                    timeout=standby_wait_interval,
                    prompt_recovery=self.prompt_recovery,
                    dialog=Dialog(connection_statement_list)
                )
                break
            except Exception as err:
                if round == standby_sync_try - 1:
                    raise Exception(
                            'Bringing standby to any state failed within {} sec'.format(standby_wait_time)) from err

            except Exception as err:
                raise SubCommandFailure("Reload failed : %s" % err) from err
            # Re-designate handles before applying config.
        # Roles could have switched as a result of the reload.
        con.connection_provider.designate_handles()
        con.active.state_machine.go_to('enable',
                                       con.active.spawn,
                                       prompt_recovery=self.prompt_recovery,
                                       context=context)

        # Issue init commands to disable console logging
        exec_commands = con.active.settings.HA_INIT_EXEC_COMMANDS
        for exec_command in exec_commands:
            con.execute(exec_command, prompt_recovery=self.prompt_recovery)
        config_commands = con.active.settings.HA_INIT_CONFIG_COMMANDS

        config_lock_retries_ori = con.settings.CONFIG_LOCK_RETRIES
        config_lock_retry_sleep_ori = con.settings.CONFIG_LOCK_RETRY_SLEEP
        con.active.settings.CONFIG_LOCK_RETRY_SLEEP = con.active.settings.CONFIG_POST_RELOAD_RETRY_DELAY_SEC
        con.active.settings.CONFIG_LOCK_RETRIES = con.active.settings.CONFIG_POST_RELOAD_MAX_RETRIES

        try:
            con.configure(config_commands,
                          target='active',
                          prompt_recovery=self.prompt_recovery)
        except Exception:
            raise
        finally:
            con.settings.CONFIG_LOCK_RETRIES = config_lock_retries_ori
            con.settings.CONFIG_LOCK_RETRY_SLEEP = config_lock_retry_sleep_ori



        con.log.info("+++ Reload Completed Successfully +++")
        self.result = True


