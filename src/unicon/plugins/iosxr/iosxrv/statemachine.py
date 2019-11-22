__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine

from unicon.plugins.iosxr.iosxrv.patterns import IOSXRVPatterns
from unicon.plugins.iosxr.statements import IOSXRStatements
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Statement, Dialog


patterns = IOSXRVPatterns()
statements = IOSXRStatements()


class IOSXRVSingleRpStateMachine(IOSXRSingleRpStateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)
        admin = State('admin', patterns.xr_admin_prompt)
        run = State('run', patterns.run_prompt)

        self.add_state(enable)
        self.add_state(config)
        self.add_state(admin)
        self.add_state(run)

        config_dialog = Dialog([
           [patterns.commit_changes_prompt, 'sendline(yes)', None, True, False],
           [patterns.commit_replace_prompt, 'sendline(yes)', None, True, False],
           [patterns.configuration_failed_message,
                self.handle_failed_config, None, True, False]
           ])

        enable_to_config = Path(enable, config, 'configure terminal', None)
        enable_to_admin = Path(enable, admin, 'admin', None)
        enable_to_run = Path(enable, run, 'run', None)
        admin_to_enable = Path(admin, enable, 'exit', None)
        run_to_enable = Path(run, enable, 'exit', None)
        config_to_enable = Path(config, enable, 'end', config_dialog)

        self.add_path(config_to_enable)
        self.add_path(enable_to_config)
        self.add_path(enable_to_admin)
        self.add_path(enable_to_run)
        self.add_path(admin_to_enable)
        self.add_path(run_to_enable)

        self.add_default_statements(self.default_commands)


class IOSXRVDualRpStateMachine(IOSXRVSingleRpStateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        super().create()

        standby_locked = State('standby_locked', patterns.standby_prompt)
        self.add_state(standby_locked)
