""" IOSXR-specific utilities. """

import re

from unicon.plugins.generic import GenericUtils
from unicon.utils import AttributeDict

class IosxrUtils(GenericUtils):

    def get_redundancy_details(self, connection, timeout=None, who='my'):
        """
        :arg  connection:  device connection object
        :return: device role and redundancy mode of the device
        """
        timeout = timeout or connection.settings.EXEC_TIMEOUT

        show_red_out = connection.execute("show redundancy", timeout=timeout)

        # Redundancy information for node 0/RSP0/CPU0:
        # Node 0/RSP0/CPU0 is in ACTIVE role
        p1 = re.compile(r'[Nn]ode +(?P<master>\S+) +is +in +(?P<state>[A-Z\s]+) +role')
        m1 = p1.search(show_red_out)
        if m1:
            master = AttributeDict()
            state = m1.groupdict().get('state', '')
            master.update({
                'role': state.lower(),
                'state': state
            })

        # Node Redundancy Partner (0/RSP1/CPU0) is in STANDBY role
        p2 = re.compile(r'[Nn]ode +[Rr]edundancy +[Pp]artner +\((?P<peer>\S+)\) '
                        r'+is +in +(?P<state>[A-Z\s]+) +role')
        m2 = p2.search(show_red_out)
        if m2:
            peer = AttributeDict()
            state = m2.groupdict().get('state', '')
            peer.update({
                'role': state.lower(),
                'state': state
            })

        return master if who == 'my' else peer

