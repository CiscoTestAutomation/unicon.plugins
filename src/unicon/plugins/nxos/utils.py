""" NXOS-specific utilities. """

import re

from unicon.plugins.generic import GenericUtils
from unicon.utils import AttributeDict

class NxosUtils(GenericUtils):

    def get_redundancy_details(self, connection, timeout=None, who='my'):
        """
        :arg  connection:  device connection object
        :return: device role and redundancy mode of the device
        """
        timeout = timeout or connection.settings.EXEC_TIMEOUT
        redundancy_details = AttributeDict()

        show_red_out = connection.execute("show redundancy status",
                                          timeout=timeout)
        if who == "peer":
            block = 'Other supervisor'
        else:
            block = "This supervisor"
        output = self.output_block_extract(data=show_red_out, block=block)
        redundancy_details['role'] = ""
        output = output.split("\n")
        for line in output:
            if re.search("Redundancy state", line):
                redundancy_details['role'] =\
                    line[line.find(":") + 1:].strip().lower()

            if redundancy_details['role'] == "not present":
                redundancy_details['state'] = 'DISABLED'

            if re.search("Internal state", line):
                mode = line[line.find(":") + 1:].strip()
                if mode == "HA standby":
                    redundancy_details['mode'] = 'sso'
                    redundancy_details['state'] = 'STANDBY HOT'
                elif mode == "Active with HA standby":
                    redundancy_details['mode'] = 'sso'
                    redundancy_details['state'] = 'STANDBY HOT'
                elif mode == "Active with no standby":
                    redundancy_details['mode'] = 'rpr'
                    redundancy_details['state'] = 'STANDBY COLD'
                else:
                    redundancy_details['mode'] = 'unknown'
                    redundancy_details['state'] = 'unknown'
        return redundancy_details

