

from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.plugins.generic.service_implementation import Execute as GenericExecute

class Rommon(GenericExecute):
    """C9800-specific Rommon service.
    Requires explicit config_register to be passed when invoked.
    No Enable Break parsing (not in C9800 show boot output).
    """
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'rommon'
        self.end_state = 'rommon'
        self.service_name = 'rommon'
        self.timeout = kwargs.get('reload_timeout', 600)
        self.__dict__.update(kwargs)

    def pre_service(self, *args, **kwargs):
        sm = self.get_sm()
        con = self.connection
        sm.go_to('enable', con.spawn, context=self.context)
        confreg = kwargs.get('config_register', "0x0")
        try:
            con.configure(f'config-register {confreg}')
        except Exception as err:
            raise SubCommandFailure(f"Failed to configure config-register {confreg}", err)

        super().pre_service(*args, **kwargs)