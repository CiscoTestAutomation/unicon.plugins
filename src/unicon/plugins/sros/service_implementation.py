__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.eal.dialogs import Dialog, Statement
from unicon.core.errors import SubCommandFailure
from unicon.plugins.generic.service_implementation import Configure, Execute

from .statements import sros_statements

KEY_RETURN_ROOT = '\x1a'


class SrosServiceMixin(object):

    def return_to_cli_root(self, state):
        handle = self.get_handle()
        state = handle.state_machine.get_state(state)
        statement = Statement(pattern=state.pattern,
                              action=None,
                              args=None,
                              loop_continue=False,
                              continue_timer=False,
                              trim_buffer=True)
        dialog = Dialog([sros_statements.discard_uncommitted, statement])
        handle.spawn.send(KEY_RETURN_ROOT)
        try:
            dialog.process(handle.spawn)
        except Exception as err:
            raise SubCommandFailure('Return to cli root failed', err) from err

    def pre_service(self, *args, **kwargs):
        self.prompt_recovery = kwargs.get('prompt_recovery', False)
        sm = self.get_sm()
        con = self.connection
        sm.go_to(self.start_state, con.spawn,
                 prompt_recovery=self.prompt_recovery,
                 context=con.context)
        self.return_to_cli_root(self.start_state)

    def post_service(self, *args, **kwargs):
        self.return_to_cli_root(self.end_state)
        super().post_service(*args, **kwargs)


class SrosMdcliExecute(SrosServiceMixin, Execute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'mdcli'
        self.end_state = 'mdcli'
        self.service_name = 'execute'


class SrosMdcliConfigure(SrosServiceMixin, Configure):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'mdcli'
        self.end_state = 'mdcli'
        self.service_name = 'config'
        self.commit_cmd = 'commit'

    def call_service(self,
                     mode,
                     command=[],
                     *args,
                     **kwargs):
        handle = self.get_handle()
        handle.spawn.sendline('configure {}'.format(mode))
        super().call_service(command, *args, **kwargs)


class SrosClassicExecute(SrosServiceMixin, Execute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'classiccli'
        self.end_state = 'classiccli'
        self.service_name = 'classic_execute'


class SrosClassicConfigure(SrosServiceMixin, Configure):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'classiccli'
        self.end_state = 'classiccli'
        self.service_name = 'classic_config'
        self.commit_cmd = ''
