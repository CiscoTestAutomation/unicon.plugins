import re

from unicon.plugins.generic import GenericSingleRpConnectionProvider
from unicon.plugins.generic import GenericDualRpConnectionProvider
from unicon.plugins.nxos.service_statements import additional_connection_dialog
from unicon.eal.dialogs import Dialog
from unicon.plugins.nxos.utils import NxosUtils

utils = NxosUtils()

class NxosSingleRpConnectionProvider(GenericSingleRpConnectionProvider):

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

    def unlock_standby(self):
        """not required on this platform"""
        pass

    def get_connection_dialog(self):
        dialog = super().get_connection_dialog()
        dialog += Dialog(additional_connection_dialog)
        return dialog

    def designate_handles(self):
        con = self.connection
        con._is_connected = True
        con.a.state_machine.go_to('enable', con.a.spawn,
                   context=con.context,
                   prompt_recovery=self.prompt_recovery,
                   timeout=con.connection_timeout,
                   dialog=self.get_connection_dialog())
        output = con.execute('show system redundancy status', target='a')
        res = utils.output_block_extract(output, 'This supervisor')
        red_match = re.search(r'[Rr]edundancy state:\s*(\S+)', res)
        if red_match:
            if red_match.groups()[0].lower() == 'active':
                con.a.role = 'active'
                con.b.role = 'standby'
            elif red_match.groups()[0].lower() == 'standby':
                con.a.role = 'standby'
                con.b.role = 'active'
            else:
                raise ConnectionError('unable to designate handles')
        con._handles_designated = True


    def assign_ha_mode(self):
        self.connection.a.mode = 'sso'
        self.connection.b.mode = 'sso'

    def disconnect(self):
        # check whether we are on vdc
        if self.connection.current_vdc:
            self.connection.log.info("device is on VDC, switching back before disconnecting")
            self.connection.switchback()
        super().disconnect()

