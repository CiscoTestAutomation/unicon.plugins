""" IOS-XE CAT9KV service implementations. """

from unicon.eal.dialogs import Dialog
from ..service_implementation import Reload as IosxeReload
from .statements import boot_from_rommon_stmt

from unicon.plugins.generic.service_statements import reload_statement_list
from unicon.plugins.generic.statements import default_statement_list
from unicon.plugins.iosxe.statements import grub_prompt_stmt


class Reload(IosxeReload):
    """CAT9KV Reload service that handles GRUB boot scenarios."""

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        # Override the service dialog to include cat9kv specific statements
        self.dialog = Dialog([boot_from_rommon_stmt, grub_prompt_stmt] +
                             reload_statement_list +
                             default_statement_list)
