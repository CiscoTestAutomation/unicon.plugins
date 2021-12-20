

import re

from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.plugins.generic.service_statements import reload_statement_list
from unicon.plugins.generic.service_implementation import (
    Execute as GenericExecute
)

from ..service_implementation import Reload as XEReload
from ..statements import boot_from_rommon_stmt


class Reload(XEReload):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog = Dialog(reload_statement_list + [boot_from_rommon_stmt])

    def pre_service(self, *args, **kwargs):
        if "image_to_boot" in kwargs:
            self.start_state = 'rommon'
        else:
            self.start_state = 'enable'

        super().pre_service(*args, **kwargs)

    def call_service(self, *args, **kwargs):
        if "image_to_boot" in kwargs:
            self.context["image_to_boot"] = kwargs["image_to_boot"]
            reload_command = "boot {}".format(
                self.context['image_to_boot']).strip()
            super().call_service(reload_command, *args, **kwargs)
            self.context.pop("image_to_boot", None)
        else:
            super().call_service(*args, **kwargs)


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
        m = re.search(r'Enable Break = (yes|no)', boot_info)
        if m:
            break_enabled = m.group(1)
            if break_enabled == 'no':
                con.configure('boot enable-break')
        else:
            raise SubCommandFailure('Could not determine if break is enabled, cannot transition to rommon')
        super().pre_service(*args, **kwargs)
