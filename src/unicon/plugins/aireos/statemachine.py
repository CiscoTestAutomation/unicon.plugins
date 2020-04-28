
from unicon.statemachine import Path, State, StateMachine
from .patterns import AireosPatterns

from unicon.plugins.generic.statements import default_statement_list


p = AireosPatterns()


class AireosStateMachine(StateMachine):
    def create(self):

        enable = State('enable', p.enable_prompt)
        show = State('show', p.show_prompt)
        config = State('config', p.config_prompt)
        debug = State('debug', p.debug_prompt)
        test_ = State('test', p.test_prompt)
        transfer = State('transfer', p.transfer_prompt)
        license_ = State('license', p.license_prompt)
        reset_ = State('reset', p.reset_prompt)
        save = State('save', p.save_prompt)
        shell = State('shell', p.shell_prompt)

        enable_to_show = Path(enable, show, 'show', None)
        enable_to_config = Path(enable, config, 'config', None)
        enable_to_debug = Path(enable, debug, 'debug', None)
        enable_to_test = Path(enable, test_, 'test', None)
        enable_to_transfer = Path(enable, transfer, 'transfer', None)
        enable_to_license = Path(enable, license_, 'license', None)
        enable_to_reset = Path(enable, reset_, 'reset', None)
        enable_to_save = Path(enable, save, 'save', None)
        enable_to_shell = Path(enable, shell, 'devshell shell', None)

        config_to_enable = Path(config, enable, 'exit', None)
        show_to_enable = Path(show, enable, 'exit', None)
        debug_to_enable = Path(debug, enable, 'end', None)
        test_to_enable = Path(test_, enable, 'exit', None)
        transfer_to_enable = Path(transfer, enable, 'exit', None)
        license_to_enable = Path(license_, enable, 'exit', None)
        reset_to_enable = Path(reset_, enable, 'exit', None)
        save_to_enable = Path(save, enable, 'exit', None)
        shell_to_enable = Path(shell, enable, 'exit', None)

        self.add_state(enable)
        self.add_state(show)
        self.add_state(config)
        self.add_state(debug)
        self.add_state(test_)
        self.add_state(transfer)
        self.add_state(license_)
        self.add_state(reset_)
        self.add_state(save)
        self.add_state(shell)

        self.add_path(enable_to_show)
        self.add_path(enable_to_config)
        self.add_path(enable_to_debug)
        self.add_path(enable_to_test)
        self.add_path(enable_to_transfer)
        self.add_path(enable_to_license)
        self.add_path(enable_to_reset)
        self.add_path(enable_to_save)
        self.add_path(enable_to_shell)

        self.add_path(show_to_enable)
        self.add_path(config_to_enable)
        self.add_path(debug_to_enable)
        self.add_path(test_to_enable)
        self.add_path(transfer_to_enable)
        self.add_path(license_to_enable)
        self.add_path(reset_to_enable)
        self.add_path(save_to_enable)
        self.add_path(shell_to_enable)

        self.add_default_statements(default_statement_list)


class AireosDualRpStateMachine(AireosStateMachine):

    def create(self):
        super().create()

        standby = State('standby', p.standby_exec)
        self.add_state(standby)
