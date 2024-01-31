#!/usr/bin/env python3

from pyats import aetest
from pyats.bringup import BringUp

class common_setup(aetest.CommonSetup):
    @aetest.subsection
    def connect(self, testbed, uut1_name, uut2_name,
                uut1_if_name, uut2_if_name):
        """ Connect to nodes in the topology """
        uut1 = testbed.devices[uut1_name]
        uut2 = testbed.devices[uut2_name]

        uut1.connect()

        uut2.connect()

        uut1.ping(uut2.interfaces[uut2_if_name].ipv4.ip.exploded)
        uut2.ping(uut1.interfaces[uut1_if_name].ipv4.ip.exploded)


if __name__ == '__main__':
    import argparse
    from pyats.topology import loader
    from pyats.aetest.main import AEtest
    import logging

    temp_aetest = AEtest()
    temp_aetest.loglevel = logging.WARNING
    temp_aetest.configureLogging()
    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('-uut1_name', dest = 'uut1_name')
    parser.add_argument('-uut2_name', dest = 'uut2_name')
    parser.add_argument('-uut1_if_name', dest = 'uut1_if_name')
    parser.add_argument('-uut2_if_name', dest = 'uut2_if_name')
    parser.add_argument('-testbed_file', dest = 'testbed_file')
    parser.add_argument('-connect_to_existing_topology', \
        dest = 'connect_to_existing_topology', action='store_true', \
        default=False)

    parsed_args, unknown = parser.parse_known_args()

    uut1_name = parsed_args.uut1_name
    uut2_name = parsed_args.uut2_name
    uut1_if_name = parsed_args.uut1_if_name
    uut2_if_name = parsed_args.uut2_if_name
    if parsed_args.connect_to_existing_topology:
        testbed = loader.load(parsed_args.testbed_file)
        aetest.main(\
            testbed = testbed, uut1_name=uut1_name, uut2_name=uut2_name,
            uut1_if_name=uut1_if_name, uut2_if_name=uut2_if_name)
    else:
        with BringUp(
                bringup_log_level='debug',
                bringup_xrut_log_level='debug') as bringup:
            testbed = loader.load(bringup.topology_config)
            aetest.main(\
                testbed = testbed, uut1_name=uut1_name, uut2_name=uut2_name,
            uut1_if_name=uut1_if_name, uut2_if_name=uut2_if_name)

