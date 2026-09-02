""" SONiC (Software for Open Networking in the Cloud) CLI implementation """

__author__ = "Liam Gerrior <lgerrior@cisco.com>"

from unicon.plugins.linux import LinuxConnection, LinuxServiceList, LinuxConnectionProvider
from unicon.plugins.linux.statemachine import LinuxStateMachine
from unicon.plugins.linux.settings import LinuxSettings


class SonicConnection(LinuxConnection):
    os = 'sonic'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = LinuxStateMachine
    connection_provider_class = LinuxConnectionProvider
    subcommand_list = LinuxServiceList
    settings = LinuxSettings()
