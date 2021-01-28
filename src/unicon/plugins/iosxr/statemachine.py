__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.statemachine import StateMachine
from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.plugins.iosxr.statements import IOSXRStatements
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Statement, Dialog


patterns = IOSXRPatterns()
statements = IOSXRStatements()

default_commands = [statements.more_prompt_stmt]


class IOSXRSingleRpStateMachine(StateMachine):

    # Make it easy for subclasses to pick these up.
    default_commands = default_commands

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)
        exclusive = State('exclusive', patterns.exclusive_prompt)
        run = State('run', patterns.run_prompt)

        admin = State('admin', patterns.admin_prompt)
        admin_conf = State('admin_conf', patterns.admin_conf_prompt)
        admin_run = State('admin_run', patterns.admin_run_prompt)

        self.add_state(enable)
        self.add_state(config)
        self.add_state(exclusive)
        self.add_state(run)
        self.add_state(admin)
        self.add_state(admin_conf)
        self.add_state(admin_run)

        config_dialog = Dialog([
           [patterns.commit_changes_prompt, 'sendline(yes)', None, True, False],
           [patterns.commit_replace_prompt, 'sendline(yes)', None, True, False],
           [patterns.configuration_failed_message,
            self.handle_failed_config, None, True, False]
           ])

        enable_to_exclusive = Path(enable, exclusive, 'configure exclusive', None)
        enable_to_config = Path(enable, config, 'configure terminal', None)
        enable_to_run = Path(enable, run, 'run', None)
        enable_to_admin = Path(enable, admin, 'admin', None)
        admin_to_admin_conf = Path(admin, admin_conf, 'config', None)
        admin_to_admin_run = Path(admin, admin_run, 'run', None)
        admin_conf_to_admin = Path(admin_conf, admin, 'exit', config_dialog)
        admin_run_to_admin = Path(admin_run, admin, 'exit', None)
        admin_to_enable = Path(admin, enable, 'exit', None)
        run_to_enable = Path(run, enable, 'exit', None)
        config_to_enable = Path(config, enable, 'end', config_dialog)
        exclusive_to_enable = Path(exclusive, enable, 'end', config_dialog)

        self.add_path(config_to_enable)
        self.add_path(enable_to_config)
        self.add_path(exclusive_to_enable)
        self.add_path(enable_to_exclusive)
        self.add_path(enable_to_admin)
        self.add_path(enable_to_run)
        self.add_path(admin_to_enable)
        self.add_path(run_to_enable)
        self.add_path(admin_to_admin_conf)
        self.add_path(admin_to_admin_run)
        self.add_path(admin_conf_to_admin)
        self.add_path(admin_run_to_admin)

        self.add_default_statements(default_commands)

    @staticmethod
    def handle_failed_config(spawn):
        spawn.read_update_buffer()
        spawn.sendline('show configuration failed')
        spawn.expect([patterns.config_prompt])
        spawn.sendline('abort')


class IOSXRDualRpStateMachine(IOSXRSingleRpStateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        super().create()

        standby_locked = State('standby_locked', patterns.standby_prompt)
        self.add_state(standby_locked)
