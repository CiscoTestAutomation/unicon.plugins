__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.service_implementation import HAReloadService

from .service_statements import ios_iol_ha_reload_statement_list


class IosIolSwitchoverService(HAReloadService):
    """iol reuses HAReloadService for SwitchoverService"""

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.command = 'redundancy switch-activity force'
        self.dialog = Dialog(ios_iol_ha_reload_statement_list)
