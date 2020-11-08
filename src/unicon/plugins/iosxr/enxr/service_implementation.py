__copyright__ = "# Copyright (c) 2019 by cisco Systems, Inc. All rights reserved."
__author__ = "ashok joshi <ashojosh@cisco.com>"

import pexpect
from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog, Statement
from unicon.core.errors import SubCommandFailure, TimeoutError
from unicon.eal.dialogs import Dialog

from unicon.plugins.generic.service_implementation import \
    Configure as GenericConfigure, \
    Execute as GenericExecute,\
    Ping as GenericPing,\
    HaConfigureService as GenericHAConfigure,\
    HaExecService as GenericHAExecute,\
    HAReloadService as GenericHAReload,\
    SwitchoverService as GenericHASwitchover, \
    Traceroute as GenericTraceroute, \
    Copy as GenericCopy, \
    ResetStandbyRP as GenericResetStandbyRP

from unicon.plugins.iosxr.statements import IOSXRStatements

statements = IOSXRStatements()

class Execute(BaseService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.prompt_recovery = connection.prompt_recovery
        self.connected = False
        self.ssh = None

    def pre_service(self, *args, **kwargs):
        # Check if connection is established
        if self.connection.is_connected:
            return
        elif self.connection.reconnect:
            self.connection.connect()
        else:
            raise ConnectionError("Connection is not established to device")

        # Bring the device to required state to issue a command.
        self.connection.state_machine.go_to(self.start_state,
                                            self.connection.spawn,
                                            context=self.connection.context)

    def call_service(self, cmd, dialog=Dialog([]), timeout=20, *args, **kwargs):
        self.connect()
        return self._send(cmd)

    def post_service(self, *args, **kwargs):
        pass

    @property
    def connected(self):
        """ Return True if session is connected."""
        return self._connected

    @connected.setter
    def connected(self, is_connected):
        self._connected = is_connected

    def connect(self, **kwargs):
        # con = self.connection
        """Connect to EnXR.
        Args:
        kwargs (dict):
            spawn (str): Spawn parameter for pexpect (default "exec").
            prompt (str): Expect parameter for pexpect (default ":ios#").
        Returns:
        (bool): True if connection is successful
        """
        try:
            if not self.connected:
                self.spawn = kwargs.get('spawn', 'exec')
                self.prompt = kwargs.get('prompt', ':ios#')
                if not self.connected:
                    p = pexpect.spawn(self.spawn)
                    p.expect(self.prompt, timeout=10)
                    self.connected = True
                    self.ssh = p

        except pexpect.exceptions.TIMEOUT:
            log.error('EnXR connect failed ')
        except Exception:
            log.error('EnXR connect failed ')
            log.error(traceback.format_exc())
        finally:
            return self.connected


    def _send(self, cmd):
        """Using pexpect for all commands."""
        if not cmd or not self.connected:
            return
        try:
            self._flush_connection()
            self.ssh.sendline(cmd)
            self.ssh.expect(self.prompt, timeout=10)
            self.result = self.ssh.before.decode('utf-8') + self.prompt
            self.connection.log.info(self.result)
        except pexpect.exceptions.TIMEOUT:
            log.error('EVxR CLI failed %s\n\n%s',
                      (self.dev_profile.base.profile_name,
                       cmd))
            self.result = 'Command TIMEOUT'

    def send_config(self, cmd):
        """Send any CLI configuration command.
        If command does not start with "conf", that will be prepended.
        If command does not end in "commit end" it will be appended.
        Args:
          cmd (str): Configuration CLI command.
          kwargs (dict): Optional arguments.
        Returns:
          (str): CLI response
        """
        if not cmd.strip().startswith('conf'):
            cmd = 'conf\r\n' + cmd
        if not cmd.strip().endswith('end'):
            if not cmd.strip().endswith('commit'):
                cmd += '\r\ncommit\r\nend\r\n'
            else:
                cmd += '\r\nend\r\n'
        return self._send(cmd)

    # def send_exec(self, cmd):
    #     """Send any CLI exec commmand.
    #     Args:
    #       cmd (str): Configuration CLI command.
    #       kwargs (dict): Optional arguments.
    #     Returns:
    #       (str): CLI response
    #     """
    #     return self._send(cmd)

    def disconnect(self):
        """Disconnect from EnXR.
        Returns:
          (bool): True if disconnect is successful
        """
        try:
            if self.connected:
                self.ssh.close()
                self.connected = False
        except Exception:
            log.error('EnXR disconnect failed %s',
                      self.dev_profile.base.profile_name)
            log.error(traceback.format_exc())
        finally:
            return self.connected

    def _flush_connection(self):
        """Spawn a new pexpect between send calls.
        The NETCONF plugin on same EnXR simulator uses a proxy executable.
        When the NETCONF proxy is used, the CLI changes do not show up in
        the pexpect pty unless it is closed and a new one is spawned.
        """
        self.disconnect()
        self.connect(spawn=self.spawn, prompt=self.prompt)