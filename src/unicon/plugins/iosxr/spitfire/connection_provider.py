__author__ = "Sritej K V R <skanakad@cisco.com>"



from unicon.plugins.iosxr.connection_provider import IOSXRSingleRpConnectionProvider,IOSXRDualRpConnectionProvider
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxr.spitfire.statements import connection_statement_list
from unicon.plugins.iosxr.spitfire.settings import SpitfireSettings
import time


class SpitfireSingleRpConnectionProvider(IOSXRSingleRpConnectionProvider):
    """ Implements Generic singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)
    
    def set_init_commands(self):
        con = self.connection

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            self.init_exec_commands = con.settings.SPITFIRE_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            self.init_config_commands = con.settings.SPITFIRE_INIT_CONFIG_COMMANDS


    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device
            Any additional Statements(prompts) to be handled during
            initial connection has to be updated here,
            connection provider uses this method to fetch connection
            dialog
        """
        con = self.connection
        return con.connect_reply + Dialog(connection_statement_list)

    def execute_init_commands(self, standby=False):
        """ Executes the initialization commands on the device.
        On standy don't execute configure commands.
        """
        self.set_init_commands()

        assert isinstance(self.init_exec_commands, list), 'Init commands must be a list'
        assert isinstance(self.init_config_commands, list), 'Init commands must be a list'

        con = self.connection

        for command in self.init_exec_commands:
            con.execute(command, prompt_recovery = self.prompt_recovery)
    
        self.check_config_lock()
        
        if not standby and len(self.init_config_commands):
            con.configure(self.init_config_commands, prompt_recovery = self.prompt_recovery)

    def check_config_lock(self,standby=False):
        """ Check if config lock is held by anyone during initial 
        connect, as this can cause initial config set to fail.
        """
        con = self.connection
        print("Checking for config lock") 
        
        t_out = SpitfireSettings.CONFIG_LOCK_TIMEOUT
        # Wait upto 10 mins for config lock to be cleared
        t_end = time.time() + t_out
        while time.time() < t_end:
            if len(con.execute("show configuration lock", prompt_recovery = self.prompt_recovery).strip().splitlines()) > 1:
                time.sleep(10)
                continue
            break
        else:
            raise Exception("Config lock not released even after 10 mins")
        
        # Wait upto 10 mins for ztp configuration lock to be done
        t_end = time.time() + t_out
        while time.time() < t_end:
            if len(con.execute("show ztp log | i 'SUCCESSFULLY'", prompt_recovery = self.prompt_recovery).strip().splitlines()) < 2:
                time.sleep(10)
                continue
            break
        else:
            raise Exception("ZTP lock not exited even after 10 mins")


class SpitfireDualRpConnectionProvider(IOSXRDualRpConnectionProvider):
    """ Implements Generic singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)
    
    def set_init_commands(self):
        con = self.connection

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            self.init_exec_commands = con.settings.SPITFIRE_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            self.init_config_commands = con.settings.SPITFIRE_INIT_CONFIG_COMMANDS


    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device
            Any additional Statements(prompts) to be handled during
            initial connection has to be updated here,
            connection provider uses this method to fetch connection
            dialog
        """
        con = self.connection
        return con.connect_reply + Dialog(connection_statement_list)
