"""
Module:
    unicon.plugins.nd

Authors:
    pyATS TEAM (pyats-support-ext@cisco.com)

Description:
    This subpackage implements ND
"""

# from unicon.plugins.linux import LinuxConnection
from unicon.plugins.linux import LinuxConnection,LinuxServiceList
from unicon.plugins.linux.statemachine import LinuxStateMachine
from unicon.plugins.linux.connection_provider import LinuxConnectionProvider
from unicon.plugins.linux.settings import LinuxSettings


# from unicon.plugins.confd import ConfdConnection, ConfdServiceList, ConfdConnectionProvider
# from unicon.plugins.confd.settings import ConfdSettings

class NDConnection(LinuxConnection):
    """
    Connection class for ND connections.
    Extends the Linux connection to function with 'nd' os.
    """
    os = 'nd'
    state_machine_class = LinuxStateMachine
    connection_provider_class = LinuxConnectionProvider
    subcommand_list = LinuxServiceList
    settings = LinuxSettings()
