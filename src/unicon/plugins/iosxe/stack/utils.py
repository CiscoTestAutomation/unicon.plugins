""" Stack utilities. """

import re
import time

from unicon.eal.dialogs import Dialog
from unicon.utils import Utils, AttributeDict

from .service_statements import send_boot


class StackUtils(Utils):

    def get_redundancy_details(self, connection, timeout=None):
        """ Get redundancy details from stack device

        Args:
            connection (`obj`): connection object
            timeout (`int`): execute timeout
        Returns:
            redundancy_details (`dict`): redundancy details of all peers
                eg: 
                    {'1': {'mac': 'bcc4.9346.7880',
                        'role': 'Member',
                        'state': 'Ready',
                        'sw_num': '1'},
                    '2': {'mac': 'bcc4.9346.9180',
                        'role': 'Standby',
                        'state': 'Ready',
                        'sw_num': '2'},
                    '3': {'mac': 'bcc4.9346.7280',
                        'role': 'Active',
                        'state': 'Ready',
                        'sw_num': '3'}}
        """
        timeout = timeout or connection.settings.EXEC_TIMEOUT
        redundancy_details = AttributeDict()

        #  1       Member   bcc4.9346.7880     1      V01     Ready
        # *2       Active   bcc4.9346.9180     3      V04     Ready
        #  4       Standby  d8b1.9009.bf80     1      V01     HA sync in progress
        p = re.compile(r'^(\*)?(?P<sw_num>[0-9])\s+(?P<role>Member|Active|Standby)\s+'
                       r'(?P<mac>[\w\.]+)\s+\d+\s+\w+\s+(?P<state>[\S\s]+)$')

        output = connection.execute("show switch", timeout=timeout)

        for line in output.splitlines():
            m = p.search(line.strip())
            if m:
                group = m.groupdict()
                redundancy_details.update({group['sw_num']: group})

        return redundancy_details


    def send_boot_cmd(self, connection, timeout, prompt_recovery, dialog=Dialog([])):
        """ Send the boot command when device come to Rommon mode 

        Args:
            connection (`obj`): connection object
            timeout (`int`): execute timeout
            prompt_recovery (`bool`): prompt_recovery flag
            dialog (`Dialog`): dialog to process
        Returns:
            None
        """
        connection.spawn.sendline()
        dialog = dialog + Dialog([send_boot])
        dialog.process(connection.spawn, timeout=timeout,
                        prompt_recovery=prompt_recovery,
                        context=connection.context)


    def boot_process(self, connection, timeout, prompt_recovery, dialog=Dialog([])):
        """ Boot up the device and bring it to disable mode

        Args:
            connection (`obj`): connection object
            timeout (`int`): execute timeout
            prompt_recovery (`bool`): prompt_recovery flag
            dialog (`Dialog`): dialog to process
        Returns:
            None
        """
        connection.spawn.sendline()
        dialog.process(connection.spawn, timeout=timeout,
                        prompt_recovery=prompt_recovery,
                        context=connection.context)
        connection.state_machine.go_to('any', connection.spawn, timeout=timeout,
                                    prompt_recovery=prompt_recovery,
                                    context=connection.context)
        connection.state_machine.go_to('disable', connection.spawn, timeout=timeout,
                                    prompt_recovery=prompt_recovery,
                                    context=connection.context)


    def is_active_standby_ready(self, connection):
        """ Check whether active and standby rp are in ready state

        Args:
            connection (`obj`): connection object
        Returns:
            result (`bool`): True if both in ready state, else False
        """
        active = ''
        standby = ''
        details = self.get_redundancy_details(connection)
        for sw_num, info in details.items():
            if info['role'] == 'Active':
                active = info.get('state')
            elif info['role'] == 'Standby':
                standby = info.get('state')

        return active == 'Ready' and standby == 'Ready'


    def is_active_ready(self, connection):
        """ Check whether active rp is in ready state

        Args:
            connection (`obj`): connection object
        Returns:
            result (`bool`): True if in ready state, else False
        """
        active = ''
        details = self.get_redundancy_details(connection)
        for sw_num, info in details.items():
            if info['role'] == 'Active':
                active = info.get('state')

        return active == 'Ready'

