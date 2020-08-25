"""
Module:
    unicon.plugins.generic

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This sub package defines the Generic Unicon plugin.
    Which implements the behavior commonly seen across
    various routers platforms, this should address
    the basic connection needs of most of the router ,
    also initialises the list of supported services

    Any platform specific deviations has
    to be implemented separately by sub classing this

    Here in this module we define the connection class
    with the following attributes

    * connections_provider_class - Class which Setups the connections
      and initializes the device handles
    * state_machine_class - statemachine to handle states and their
      transitions
    * subcommand_list = Supported services list
    * settings = Generic settings to setup the unicon env required
      for generic connection

"""
from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.bases.routers.connection import BaseDualRpConnection
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from unicon.plugins.generic.statemachine import GenericDualRpStateMachine
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider
from unicon.plugins.generic.connection_provider import GenericDualRpConnectionProvider
from unicon.plugins.generic.settings import GenericSettings
from unicon.plugins.generic.utils import GenericUtils
from unicon.plugins.generic import service_implementation as svc


class ServiceList:
    """ Generic single rp services. """

    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.transmit = svc.Send
        self.receive = svc.ReceiveService
        self.receive_buffer = svc.ReceiveBufferService
        self.expect = svc.Expect
        self.execute = svc.Execute
        self.config = svc.Config
        self.configure = svc.Configure
        self.enable = svc.Enable
        self.disable = svc.Disable
        self.reload = svc.Reload
        self.ping = svc.Ping
        self.traceroute = svc.Traceroute
        self.copy = svc.Copy
        self.log_user = svc.LogUser
        self.log_file = svc.LogFile
        self.expect_log = svc.ExpectLogging


class HAServiceList(ServiceList):
    """ Generic dual rp services. """

    def __init__(self):
        super().__init__()
        self.execute = svc.HaExecService
        self.config = svc.HaConfigure
        self.configure = svc.HaConfigureService
        self.get_config = svc.GetConfig
        self.get_mode = svc.GetMode
        self.get_rp_state = svc.GetRPState
        self.reload = svc.HAReloadService
        self.sync_state = svc.SyncState
        self.switchover = svc.SwitchoverService
        self.reset_standby_rp = svc.ResetStandbyRP


class GenericSingleRpConnection(BaseSingleRpConnection):
    """ Defines Generic Connection class for singleRP """
    os = 'generic'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = GenericSingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = ServiceList
    settings = GenericSettings()


class GenericDualRPConnection(BaseDualRpConnection):

    """ Defines Generic Connection class for DualRP """
    os = 'generic'
    series = None
    chassis_type = 'dual_rp'
    state_machine_class = GenericDualRpStateMachine
    connection_provider_class = GenericDualRpConnectionProvider
    subcommand_list = HAServiceList
    settings = GenericSettings()

