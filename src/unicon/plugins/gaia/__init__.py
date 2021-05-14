'''
Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider
from unicon.plugins.generic import GenericSingleRpConnection, ServiceList
from unicon.plugins.generic import service_implementation as svc
from unicon.plugins.linux import service_implementation as linux_svc
from unicon.plugins.gaia import service_implementation as gaia_svc
from unicon.plugins.gaia.statemachine import GaiaStateMachine
from unicon.plugins.gaia.settings import GaiaSettings
from time import sleep


class GaiaConnectionProvider(GenericSingleRpConnectionProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # used for tracking the initial state - it impacts the commands used
        # for state changes
        self.initial_state = ''

    def init_handle(self):
        con = self.connection

        self.initial_state = con.state_machine.current_state

        # The state machine path commands are different depending on the
        # initial state. If the default shell is configured to be 'expert'
        # mode the path commands are:
        #   'clish' for expert -> clish
        #   'exit' for clish -> expert

        # If the initial state is determined to be 'expert' mode, the
        # commands are updated and the switchto service is used to put
        # the gateway into clish mode.

        if self.initial_state == 'expert':
            path = con.state_machine.get_path('clish', 'expert')
            path.command = 'exit'

            path = con.state_machine.get_path('expert', 'clish')
            path.command = 'clish'

            # switch to clish if in expert on connect
            con.switchto('clish')

        if self.connection.goto_enable:
            con.state_machine.go_to('clish',
                                    self.connection.spawn,
                                    context=self.connection.context,
                                    prompt_recovery=self.prompt_recovery,
                                    timeout=self.connection.connection_timeout)

        self.execute_init_commands()

    def disconnect(self):
        """ Logout and disconnect from the device
        """

        con = self.connection
        if con.connected:
            con.log.info('disconnecting...')
            con.switchto(self.initial_state)
            con.sendline('exit')
            sleep(2)
            con.log.info('closing connection...')
            con.spawn.close()


class GaiaServiceList(ServiceList):
    """ gaia services """
    def __init__(self):
        super().__init__()

        self.execute = gaia_svc.GaiaExecute
        self.sendline = svc.Sendline
        self.ping = linux_svc.Ping
        self.traceroute = gaia_svc.GaiaTraceroute
        self.switchto = gaia_svc.GaiaSwitchTo


class GaiaConnection(GenericSingleRpConnection):
    """
    Connection class for Gaia OS connections
    """

    os = 'gaia'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = GaiaStateMachine
    connection_provider_class = GaiaConnectionProvider
    subcommand_list = GaiaServiceList
    settings = GaiaSettings()
