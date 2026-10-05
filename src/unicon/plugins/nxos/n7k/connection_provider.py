__author__ = 'Dave Wapstra <dwapstra@cisco.com>'

import re

from unicon.plugins.nxos import NxosSingleRpConnectionProvider, NxosDualRpConnectionProvider
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.nxos.utils import NxosUtils
from unicon.plugins.generic.statements import more_prompt_handler
from unicon.plugins.generic.patterns import GenericPatterns

utils = NxosUtils()
generic_patterns = GenericPatterns()


class Nxos7kSingleRpConnectionProvider(NxosSingleRpConnectionProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # in case device is on a vdc, this should be updated.
        self.connection.current_vdc = None

    def establish_connection(self, connection_dialog=None,
                             skip_initialization=False):
        """Detect the initial Nexus state and update VDC context.

        Args:
            connection_dialog (Dialog, optional): Replacement dialog for
                initial state detection. When omitted, the normal provider
                dialog is used.
            skip_initialization (bool): Stop after initial state detection.
        """
        establish_kwargs = {}
        if connection_dialog is not None:
            establish_kwargs['connection_dialog'] = connection_dialog
        if skip_initialization:
            establish_kwargs['skip_initialization'] = True
        super().establish_connection(**establish_kwargs)
        if skip_initialization:
            return
        con = self.connection
        m = con.spawn.match.last_match

        dialog = Dialog([
            Statement(pattern=generic_patterns.more_prompt,
                      action=more_prompt_handler,
                      loop_continue=True,
                      trim_buffer=False),
            Statement(pattern=r'.+#\s*$')
        ])

        hostname = m.groupdict().get('hostname00')
        if hostname and '-' in hostname:
            con.log.info('We may be on a VDC, checking')
            con.sendline('show vdc')
            dialog.process(con.spawn)
            vdc_info = con.spawn.match.match_output
            m = re.search(r'^1', vdc_info, re.MULTILINE)
            if m:
                con.log.info('Current VDC: Admin')
            else:
                m = re.search(r'^[2345678]\s*(?P<vdc_name>\S+)', vdc_info, re.MULTILINE)
                if m:
                    vdc_name = m.groupdict()['vdc_name']
                    con.log.info('Current VDC {}'.format(vdc_name))
                    con.current_vdc = vdc_name
                    con.hostname = con.hostname.replace('-' + vdc_name, '')
                    vdc_hostname = con.hostname + '-' + vdc_name
                    if con.is_ha:
                        con.active.state_machine.hostname = vdc_hostname
                        con.standby.state_machine.hostname = vdc_hostname
                    else:
                        con.state_machine.hostname = vdc_hostname


class Nxos7kDualRpConnectionProvider(NxosDualRpConnectionProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # in case device is on a vdc, this should be updated.
        self.connection.current_vdc = None
