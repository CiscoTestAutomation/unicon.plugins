

import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from unicon.eal.dialogs import Dialog, Statement
from unicon.core.errors import ConnectionError, SubCommandFailure
from unicon.plugins.generic.service_statements import (
    reload_statement_list,
    ha_reload_statement_list)
from unicon.plugins.generic.service_implementation import (
    Execute as GenericExecute,
    HAReloadService as GenericHAReloadService
)

from ..service_implementation import Reload as XEReload
from ..statements import boot_from_rommon_stmt, fast_reload_confirm_stmt
from .statements import boot_interrupt_stmt


class Reload(XEReload):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        # Override the service dialog
        self.dialog = Dialog(reload_statement_list + [boot_from_rommon_stmt, fast_reload_confirm_stmt])

    def pre_service(self, *args, **kwargs):
        if "image_to_boot" in kwargs:
            self.start_state = 'rommon'
            if 'image_to_boot' in self.context:
                self.context['orig_image_to_boot'] = self.context['image_to_boot']
            self.context["image_to_boot"] = kwargs["image_to_boot"]
            self.connection.log.info("'image_to_boot' specified with reload, transitioning to 'rommon' state")
        else:
            if 'image' in kwargs:
                self.context['image_to_boot'] = kwargs.get('image')
            self.start_state = 'enable'

        super().pre_service(*args, **kwargs)

    def call_service(self, *args, **kwargs):
        # assume the device is in rommon if image_to_boot is passed
        # update reload command to use rommon boot syntax
        if "image_to_boot" in kwargs:
            if 'rommon_vars' in kwargs and self.connection.state_machine.current_state == 'rommon':
                self.connection.execute([f'set {k}={v}' for k, v in kwargs['rommon_vars'].items()])
            self.context["image_to_boot"] = kwargs["image_to_boot"]
            reload_command = "boot {}".format(
                self.context['image_to_boot']).strip()
            super().call_service(reload_command, *args, **kwargs)
            self.context.pop("image_to_boot", None)
        else:
            super().call_service(*args, **kwargs)

    def post_service(self, *args, **kwargs):
        if 'orig_image_to_boot' in self.context:
            self.context['image_to_boot'] = self.context.pop('orig_image_to_boot')
        super().post_service(*args, **kwargs)


class HAReloadService(GenericHAReloadService):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog = Dialog(ha_reload_statement_list + [boot_from_rommon_stmt])

    def pre_service(self, *args, **kwargs):
        if "image_to_boot" in kwargs:
            if 'rommon_vars' in kwargs and all(con.state_machine.current_state == 'rommon' for con in self.connection._subconnections):
                for con in self.connection._subconnections:
                    con.execute([f'set {k}={v}' for k, v in kwargs['rommon_vars'].items()])
            self.start_state = 'rommon'
            if 'image_to_boot' in self.context:
                self.context['orig_image_to_boot'] = self.context['image_to_boot']
            self.context["image_to_boot"] = kwargs["image_to_boot"]
            self.connection.active.context.update({
                "image_to_boot": self.context["image_to_boot"]
            })
            self.connection.standby.context.update({
                "image_to_boot": self.context["image_to_boot"]
            })
            self.connection.log.info("'image_to_boot' specified with reload, transitioning to 'rommon' state")
        else:
            if 'image' in kwargs:
                self.context['image_to_boot'] = kwargs.get('image')
                self.connection.active.context.update({
                "image_to_boot": self.context["image_to_boot"]
                })
                self.connection.standby.context.update({
                    "image_to_boot": self.context["image_to_boot"]
                })
            self.start_state = 'enable'

        super().pre_service(*args, **kwargs)

    def call_service(self, *args, **kwargs):
        # assume the device is in rommon if image_to_boot is passed
        # update reload command to use rommon boot syntax
        if "image_to_boot" in kwargs:
            reload_command = "boot {}".format(
                self.context['image_to_boot']).strip()
            super().call_service(reload_command, *args, **kwargs)
            self.context.pop("image_to_boot", None)
        else:
            super().call_service(*args, **kwargs)

    def post_service(self, *args, **kwargs):
        if 'orig_image_to_boot' in self.context:
            self.context['image_to_boot'] = self.context.pop('orig_image_to_boot')
        self.connection.active.context.pop('image_to_boot', None)
        self.connection.standby.context.pop('image_to_boot', None)
        super().post_service(*args, **kwargs)


class Rommon(GenericExecute):
    """ Brings device to the Rommon prompt and executes commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'rommon'
        self.end_state = 'rommon'
        self.service_name = 'rommon'
        self.timeout = 600
        self.__dict__.update(kwargs)

    def pre_service(self, *args, **kwargs):
        sm = self.get_sm()
        con = self.connection
        sm.go_to('enable',
                 con.spawn,
                 context=self.context)
        boot_info = con.execute('show boot')
        m = re.search(r'Enable Break = (yes|no|0|1)|ENABLE_BREAK variable (= yes|= no|does not exist)', boot_info)
        if m:
            break_enabled = m.group()
            if all(i not in break_enabled for i in ['yes', '1']):
                con.configure('boot enable-break')
        else:
            raise SubCommandFailure('Could not determine if break is enabled, cannot transition to rommon')
        super().pre_service(*args, **kwargs)


class HARommon(Rommon):
    """Brings device to rommon on HA systems.
    """
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def pre_service(self, *args, **kwargs):
        """Prepare HA device for rommon entry.

        Steps:
        1) Ensure prompt recovery/connection is ready.
        2) Resolve the active RP handle (fails if active cannot be determined).
        3) Detect state for all consoles.
        4) If active is already in rommon, validate if all consoles are in rommon and return.
        5) Check break enable on active.
        6) Trigger reload from active and break to rommon on each console in parallel.
        7) Validate that all consoles report rommon.

        Raises:
        - ConnectionError: when reconnect is not allowed or connection fails.
        - SubCommandFailure: when active cannot be resolved, break enable state
            cannot be determined, or any console fails to reach rommon.
        """
        # Step 1: Ensure prompt recovery/connection is ready.
        con = self.connection
        self.prompt_recovery = con.prompt_recovery
        if 'prompt_recovery' in kwargs:
            self.prompt_recovery = kwargs.get('prompt_recovery')
        if not con.is_connected:
            if not con.reconnect:
                raise ConnectionError("Connection is not established to device")
            con.log.warning('+++ Reconnecting +++')
            con.connect()

        # Step 2: Resolve the active RP handle (fails if active cannot be determined).
        subconnections = list(con._subconnections.values())
        active_subcon = getattr(con, 'active', None)
        if active_subcon is None:
            raise SubCommandFailure('Active connection is not set; cannot continue')

        # Step 3: Detect state for all consoles.
        for subcon in subconnections:
            subcon.state_machine.detect_state(subcon.spawn, context=subcon.context)

        # Step 4: If active is already in rommon, validate if all consoles are in rommon and return.
        if active_subcon.state_machine.current_state == 'rommon':
            non_rommon = []
            for subcon in subconnections:
                if subcon.state_machine.current_state != 'rommon':
                    non_rommon.append(subcon.alias)
            if non_rommon:
                raise SubCommandFailure(
                    'Active already in rommon but other connections are not: {}'.format(
                        ', '.join(non_rommon)
                    )
                )
            con.log.info('All connections already in rommon; skipping reload/break flow')
            return

        # Step 5: Check break enable on active.
        active_subcon.state_machine.go_to(
            'enable', active_subcon.spawn, context=active_subcon.context
        )
        con.log.info('Checking break enable on active %s', active_subcon.alias)
        boot_info = active_subcon.execute('show boot')
        m = re.search(
            r'Enable Break = (yes|no|0|1)|ENABLE_BREAK variable (= yes|= no|does not exist)',
            boot_info,
        )
        if m:
            break_enabled = m.group()
            if all(i not in break_enabled for i in ['yes', '1']):
                active_subcon.configure('boot enable-break')
        else:
            raise SubCommandFailure(
                f"Could not determine if break is enabled on {active_subcon.alias}, "
                "cannot transition to rommon"
            )

        # Step 6: Trigger reload from active and break to rommon on each console in parallel.
        rommon_timeout = kwargs.get('rommon_timeout', self.timeout)

        # Prepare worker function to reload active subcon if not already in rommon
        def active_reload_to_rommon():
            con.log.info('Reloading from active %s', active_subcon.alias)
            active_subcon.state_machine.go_to(
                'rommon',
                active_subcon.spawn,
                context=active_subcon.context,
                prompt_recovery=active_subcon.prompt_recovery,
                timeout=rommon_timeout,
            )

        # Prepare worker function to break to rommon on standby/other connections
        rommon_pattern = active_subcon.state_machine.get_state('rommon').pattern
        break_dialog = Dialog([
            boot_interrupt_stmt,
            Statement(
                pattern=rommon_pattern,
                action=None,
                loop_continue=False,
                continue_timer=False,
                trim_buffer=True,
            ),
        ])

        def break_to_rommon(subcon):
            con.log.info('Waiting for boot interrupt on %s', subcon.alias)
            break_dialog.process(
                subcon.spawn,
                context=subcon.context,
                prompt_recovery=subcon.prompt_recovery,
                timeout=rommon_timeout,
            )

        tasks = []
        if active_subcon.state_machine.current_state != 'rommon':
            tasks.append((active_reload_to_rommon, ()))
            for subcon in subconnections:
                if subcon is not active_subcon and subcon.state_machine.current_state != 'rommon':
                    tasks.append((break_to_rommon, (subcon,)))

        con.log.info('Transitioning %d subconnections to rommon in parallel', len(tasks))
        if tasks:
            with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
                futures = [executor.submit(func, *args) for func, args in tasks]
                for future in as_completed(futures):
                    future.result()

        # Step 7: Validate that all consoles report rommon.
        non_rommon = []
        for subcon in subconnections:
            subcon.state_machine.detect_state(subcon.spawn, context=subcon.context)
            con.log.debug('%s in state: %s', subcon.alias, subcon.state_machine.current_state)
            if subcon.state_machine.current_state != 'rommon':
                non_rommon.append(subcon.alias)
        if non_rommon:
            raise SubCommandFailure(
                'Failed to transition the following subconnections to rommon: {}'.format(
                    ', '.join(non_rommon)
                )
            )