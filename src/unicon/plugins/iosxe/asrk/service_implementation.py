""" ASRK IOS-XE HA Reload service implementation.

Uses ThreadPoolExecutor to process active and standby RP boot
dialogs in parallel, preventing standby timeout errors during reload.
"""

import logging
import warnings
from time import sleep
from concurrent.futures import ThreadPoolExecutor, wait as wait_futures, ALL_COMPLETED

from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.logs import UniconStreamHandler, UNICON_LOG_FORMAT
from unicon.plugins.generic.statements import custom_auth_statements
from unicon.plugins.generic.service_implementation import ReloadResult
from unicon.plugins.generic.utils import GenericUtils

from unicon.plugins.iosxe.service_implementation import HAReload as IosXEHAReload

utils = GenericUtils()


class HAReload(IosXEHAReload):
    """ASRK-specific HA Reload service.

    Overrides call_service to use ThreadPoolExecutor for processing
    active and standby RP boot dialogs in parallel. This prevents the
    standby spawn buffer from accumulating unprocessed boot output that
    causes timeout errors during the config sync wait phase.
    """

    def call_service(self, command=[], reload_command=[], reply=Dialog([]),
                     timeout=None, *args, **kwargs):
        con = self.connection
        sm = self.get_sm()

        # --- IOS-XE specific: image_to_boot, boot_cmd ---
        self.context["image_to_boot"] = \
            kwargs.pop("image_to_boot", kwargs.pop('image', ''))

        if sm.current_state == 'rommon' and reload_command:
            con.active.context['boot_cmd'] = reload_command

        # Determine the reload command
        if command:
            reload_cmd = command or "reload"
        else:
            reload_cmd = reload_command or "reload"

        # --- Parameters from kwargs ---
        dialog = kwargs.pop('dialog', Dialog([]))
        return_output = kwargs.pop('return_output', False)
        reload_creds = kwargs.pop('reload_creds', None)
        target_standby_state = kwargs.pop('target_standby_state', 'STANDBY HOT')
        error_pattern = kwargs.pop('error_pattern', None)
        append_error_pattern = kwargs.pop('append_error_pattern', None)

        # --- Error pattern setup ---
        if error_pattern is None:
            self.error_pattern = con.settings.ERROR_PATTERN
        else:
            self.error_pattern = error_pattern
        if not isinstance(self.error_pattern, list):
            raise ValueError('error_pattern should be a list')
        if append_error_pattern:
            if not isinstance(append_error_pattern, list):
                raise ValueError('append_error_pattern should be a list')
            self.error_pattern += append_error_pattern

        # --- Log buffer setup ---
        lb = UniconStreamHandler(self.log_buffer)
        lb.setFormatter(logging.Formatter(fmt=UNICON_LOG_FORMAT))
        con.log.addHandler(lb)
        for subcon in con.subconnections:
            subcon.log.addHandler(lb)
        self.log_buffer.seek(0)
        self.log_buffer.truncate()

        # --- Dialog handling ---
        if reply:
            if dialog:
                con.log.warning("**** Both 'reply' and 'dialog' were provided "
                                "to the reload service.  Ignoring 'dialog'.")
            dialog = reply
        elif dialog:
            warnings.warn('**** "dialog" parameter is deprecated. '
                          'Use "reply" instead. ****',
                          category=DeprecationWarning)

        timeout = timeout or self.timeout
        fmt_str = "+++ reloading %s with reload_command '%s' and timeout is %s +++"
        con.log.info(fmt_str % (con.hostname, reload_cmd, timeout))

        dialog += self.dialog
        custom_auth_stmt = custom_auth_statements(
            con.settings.LOGIN_PROMPT, con.settings.PASSWORD_PROMPT)

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

        # --- Send reload command ---
        if reload_cmd:
            con.active.spawn.sendline(reload_cmd)

        try:
            # --- Define parallel tasks ---
            active_result = {}

            def process_active():
                """Process reload dialog on active RP and bring to 'any' state."""
                reload_output = dialog.process(
                    con.active.spawn,
                    context=context,
                    prompt_recovery=self.prompt_recovery,
                    timeout=timeout)
                active_result['output'] = reload_output

                con.active.state_machine.go_to(
                    'any',
                    con.active.spawn,
                    prompt_recovery=self.prompt_recovery,
                    timeout=con.connection_timeout,
                    context=context)

            def process_standby():
                """Consume boot output from standby RP spawn."""
                con.log.info('Processing standby RP boot output in parallel')
                try:
                    dialog.process(
                        con.standby.spawn,
                        context=sby_context,
                        prompt_recovery=self.prompt_recovery,
                        timeout=timeout)
                except Exception:
                    con.log.warning(
                        'Standby dialog processing did not match any '
                        'statement, continuing with state discovery')

            # --- Process both RPs in parallel ---
            con.log.info('Processing active and standby reload in parallel')
            executor = ThreadPoolExecutor(max_workers=2)
            active_future = executor.submit(process_active)
            standby_future = executor.submit(process_standby)

            wait_futures([active_future, standby_future],
                         timeout=timeout, return_when=ALL_COMPLETED)

            # Re-raise active thread exceptions
            if active_future.exception():
                raise active_future.exception()

            # Set reload result from active processing
            if 'output' in active_result:
                self.result = active_result['output'].match_output
                self.get_service_result()

            # --- Bring standby to good state (sequentially, after threads done) ---
            con.log.info('Waiting for config sync to finish')
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
                        dialog=con.connection_provider.get_connection_dialog()
                    )
                    break
                except Exception as err:
                    if round == standby_sync_try - 1:
                        raise Exception(
                            'Bringing standby to any state failed within {} sec'
                            .format(standby_wait_time)) from err

            # If standby is in rommon, transition to disable state
            if con.standby.state_machine.current_state == 'rommon':
                con.log.info('Standby is in ROMMON state, transitioning to disable mode')
                con.standby.state_machine.go_to(
                    'disable',
                    con.standby.spawn,
                    context=sby_context,
                    timeout=timeout,
                    prompt_recovery=self.prompt_recovery,
                    dialog=con.connection_provider.get_connection_dialog()
                )

        except Exception as err:
            if hasattr(con.device, 'clean') \
                    and hasattr(con.device.clean, 'device_recovery') \
                    and con.device.clean.device_recovery.get('golden_image'):
                con.log.error(
                    'Reload failed booting device using golden image: '
                    '{}'.format(con.device.clean.device_recovery['golden_image']))
                con.device.api.device_recovery_boot(
                    golden_image=con.device.clean.device_recovery['golden_image'])
                con.log.info('Successfully booted the device using golden image.')
            raise SubCommandFailure('Reload failed : {}'.format(err))

        con.disconnect()
        con.connect()

        # Issue init commands to disable console logging
        exec_commands = con.active.settings.HA_INIT_EXEC_COMMANDS
        for exec_command in exec_commands:
            con.execute(exec_command, prompt_recovery=self.prompt_recovery)
        config_commands = con.active.settings.HA_INIT_CONFIG_COMMANDS

        config_lock_retries_ori = con.settings.CONFIG_LOCK_RETRIES
        config_lock_retry_sleep_ori = con.settings.CONFIG_LOCK_RETRY_SLEEP
        con.active.settings.CONFIG_LOCK_RETRY_SLEEP = \
            con.active.settings.CONFIG_POST_RELOAD_RETRY_DELAY_SEC
        con.active.settings.CONFIG_LOCK_RETRIES = \
            con.active.settings.CONFIG_POST_RELOAD_MAX_RETRIES

        try:
            con.configure(config_commands,
                          target='active',
                          prompt_recovery=self.prompt_recovery)
        except Exception:
            raise
        finally:
            con.settings.CONFIG_LOCK_RETRIES = config_lock_retries_ori
            con.settings.CONFIG_LOCK_RETRY_SLEEP = config_lock_retry_sleep_ori

        # Check active and standby RP are ready using show redundancy
        con.log.info('Wait for Active and Standby RP to be ready.')
        interval = con.settings.RELOAD_POSTCHECK_INTERVAL \
            if hasattr(con.settings, 'RELOAD_POSTCHECK_INTERVAL') else 30
        if utils.is_active_standby_ready(con, timeout=timeout, interval=interval):
            con.log.info('Active and Standby RPs are ready.')
        else:
            con.log.info('Timeout in %s secs. '
                'Standby RP is not in STANDBY HOT state.' % timeout)

        con.log.info("+++ Reload Completed Successfully +++")
        self.log_buffer.seek(0)
        reload_output = self.log_buffer.read()
        self.log_buffer.truncate()

        con.log.removeHandler(lb)
        for subcon in con.subconnections:
            subcon.log.removeHandler(lb)

        self.result = True
        if return_output:
            self.result = ReloadResult(self.result, reload_output)
