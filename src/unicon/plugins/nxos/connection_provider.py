import re

from unicon.plugins.generic import GenericSingleRpConnectionProvider
from unicon.plugins.generic import GenericDualRpConnectionProvider
from unicon.plugins.nxos.service_statements import additional_connection_dialog
from unicon.eal.dialogs import Dialog
from unicon.plugins.nxos.utils import NxosUtils

utils = NxosUtils()

class NxosSingleRpConnectionProvider(GenericSingleRpConnectionProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # in case device is on a vdc, this should be updated.
        self.connection.current_vdc = None

    def get_connection_dialog(self):
        dialog = super().get_connection_dialog()
        dialog += Dialog(additional_connection_dialog)
        return dialog

    def disconnect(self):
        # check whether we are on vdc
        if self.connection.current_vdc:
            self.connection.log.info("device is on VDC, switching back before disconnecting")
            self.connection.switchback()

        super().disconnect()


class NxosDualRpConnectionProvider(GenericDualRpConnectionProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # in case device is on a vdc, this should be updated.
        self.connection.current_vdc = None

    def unlock_standby(self):
        """not required on this platform"""
        pass

    def get_connection_dialog(self):
        dialog = super().get_connection_dialog()
        dialog += Dialog(additional_connection_dialog)
        return dialog

    def designate_handles(self):
        con = self.connection
        subcons = list(con._subconnections.items())
        subcon1_alias, subcon1 = subcons[0]
        subcon2_alias, subcon2 = subcons[1]

        subcon1.state_machine.go_to('enable', subcon1.spawn,
                   context=subcon1.context,
                   prompt_recovery=subcon1.prompt_recovery,
                   timeout=subcon1.connection_timeout,
                   dialog=self.get_connection_dialog())
        output = subcon1.execute('show system redundancy status')
        res = utils.output_block_extract(output, 'This supervisor')
        red_match = re.search(r'[Rr]edundancy state:\s*(\S+)', res)
        if red_match:
            if red_match.groups()[0].lower() == 'active':
                con._set_active_alias(subcon1_alias)
                con._set_standby_alias(subcon2_alias)
            elif red_match.groups()[0].lower() == 'standby':
                con._set_active_alias(subcon2_alias)
                con._set_standby_alias(subcon1_alias)
            else:
                raise ConnectionError('unable to designate handles')
        con._handles_designated = True


    def assign_ha_mode(self):
        for subconnection in self.connection.subconnections:
            subconnection.mode = 'sso'


    def disconnect(self):
        # check whether we are on vdc
        if self.connection.current_vdc:
            self.connection.log.info("device is on VDC, switching back before disconnecting")
            self.connection.switchback()
        super().disconnect()

