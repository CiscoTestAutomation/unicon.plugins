""" Quad Utilities """

import re

from unicon.plugins.iosxe.stack.utils import StackUtils


class QuadUtils(StackUtils):

    def is_peer_standby_hot(self, connection, timeout=None):
        """ Check whether peer rp is in STANDBY HOT state

        Args:
            connection (`obj`): connection object
            timeout (`int`): execute timeout
        Returns:
            result (`bool`): True if peer in STANDBY HOT state, else False
        """
        timeout = timeout or connection.settings.EXEC_TIMEOUT

        output = connection.execute("show redundancy states | in peer",
                                            timeout=timeout)

        if 'STANDBY HOT' in output:
            return True
        else:
            return False
