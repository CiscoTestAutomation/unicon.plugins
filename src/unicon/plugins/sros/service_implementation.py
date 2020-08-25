__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog, Statement
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

    def log_service_call(self):
        BaseService.log_service_call(self)

    def pre_service(self, *args, **kwargs):
        self.prompt_recovery = kwargs.get('prompt_recovery', False)
        sm = self.get_sm()
        con = self.connection
        sm.go_to(self.start_state,
                 con.spawn,
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


class SrosMdcliConfigure(SrosServiceMixin, Configure):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'mdcli'
        self.end_state = 'mdcli'
        self.commit_cmd = 'commit'
        self.mode = connection.settings.MDCLI_CONFIGURE_DEFAULT_MODE

    def call_service(self,
                     *args,
                     mode='',
                     **kwargs):
        mode = mode or self.mode
        handle = self.get_handle()
        handle.spawn.sendline('configure {}'.format(mode))
        super().call_service(*args, **kwargs)


class SrosClassiccliExecute(SrosServiceMixin, Execute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'classiccli'
        self.end_state = 'classiccli'


class SrosClassiccliConfigure(SrosServiceMixin, Configure):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'classiccli'
        self.end_state = 'classiccli'
        self.commit_cmd = ''


class SrosExecute(BaseService):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.execute_map = {'classiccli': 'classiccli_execute',
                            'mdcli': 'mdcli_execute'}

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, *args, **kwargs):
        handle = self.get_handle()
        state = handle.state_machine.current_state
        execute = getattr(self.connection, self.execute_map[state])
        self.result = execute(*args, **kwargs)


class SrosConfigure(BaseService):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.configure_map = {'classiccli': 'classiccli_configure',
                              'mdcli': 'mdcli_configure'}

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, *args, **kwargs):
        handle = self.get_handle()
        state = handle.state_machine.current_state
        configure = getattr(self.connection, self.configure_map[state])
        self.result = configure(*args, **kwargs)


class SrosSwitchCliEngine(BaseService):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, engine, *args, **kwargs):
        self.prompt_recovery = kwargs.get('prompt_recovery', False)
        sm = self.get_sm()
        con = self.connection
        sm.go_to(engine,
                 con.spawn,
                 prompt_recovery=self.prompt_recovery,
                 context=con.context)
        self.result = True

    def get_service_result(self):
        return self.result


class SrosGetCliEngine(BaseService):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, *args, **kwargs):
        handle = self.get_handle()
        self.result = handle.state_machine.current_state

    def get_service_result(self):
        return self.result
