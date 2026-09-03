#!/usr/bin/env python3

from pyats import aetest
from pyats.bringup import BringUp
import re, logging

# NOTE: uut1 device must be Moonshine for this test to work.

class common_setup(aetest.CommonSetup):
    def if_name_brief(self, if_name):
        """ Returns brief form of the interface name, if one exists """
        if "GigabitEthernet" in if_name:
            brief_name = if_name.replace("GigabitEthernet", "Gi")
        elif "Loopback" in if_name:
            brief_name = if_name.replace("Loopback", "Lo")
        else:
            brief_name = if_name

        return(brief_name)

    @aetest.subsection
    def connect_and_test(self, testbed, uut1_name, uut2_name,
                uut1_if_name, uut2_if_name):
        """ Connect to nodes in the topology """
        uut1 = testbed.devices[uut1_name]
        uut2 = testbed.devices[uut2_name]

        uut1.connect()
        uut2.connect()

        # Check that we are currently in enable state
        try:
            assert uut1.state_machine.current_state == "enable"
        except AttributeError:
            logging.log(temp_aetest.loglevel, "NOTE: uut1 has to be a Moonshine device")
            raise
        some_interface = uut1.interfaces.names.pop()
        brief_if_name = self.if_name_brief(some_interface)

        # Check output of "show interfaces" 
        output = uut1.execute("show interfaces brief")
        match = re.search("{} *up *up".format(brief_if_name), output)
        assert match

        # Apply some config (shut an interface)
        uut1.configure(['interface {}'.format(some_interface), 'shut'])

        # Check output of "show interfaces" again
        output = uut1.execute("show interfaces brief")
        match = re.search("{} *admin-down *admin-down".format(brief_if_name), output)
        assert match
 
        # Restore config
        uut1.configure(['interface {}'.format(some_interface), 'no shut'])
        


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

