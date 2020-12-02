__copyright__ = "# Copyright (c) 2019 by cisco Systems, Inc. " \
                "All rights reserved."
__author__ = "ashok joshi <ashojosh@cisco.com>"

from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog
from unicon.eal.expect import Spawn
import pexpect


class Execute(BaseService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.prompt_recovery = connection.prompt_recovery

    def pre_service(self, *args, **kwargs):
        # Check if connection is established
        if self.connection.is_connected:
            return
        if self.connection.reconnect:
            self.connection.connect()
        else:
            raise ConnectionError("Connection is not established to device")

        # Bring the device to required state to issue a command.
        self.connection.state_machine.go_to(self.start_state,
                                            self.connection.spawn,
                                            context=self.connection.context)

    def call_service(self, cmd, dialog=Dialog([]),
                     timeout=20, *args, **kwargs):
        try:
            # self._flush_connection()
            con = self.connection.connection_provider
            con.ssh.sendline(cmd)
            con.ssh.expect(con.prompt, timeout=10)
            self.result = con.ssh.before.decode('utf-8') + con.prompt
            self.connection.log.info(self.result)
        except pexpect.exceptions.TIMEOUT:
            self.connection.log.warning('EnxR CLI failed %s\n\n%s', cmd)
            self.result = 'Command TIMEOUT'

    def post_service(self, *args, **kwargs):
        pass

    def get_service_result(self):
        return self.result

    def _send(self, cmd):
        """Using pexpect for all commands."""
        # if not cmd or not self.connected:
        #     return
        try:
            # self._flush_connection()
            con = self.connection.connection_provider
            con.ssh.sendline(cmd)
            con.ssh.expect(con.prompt, timeout=10)
            self.result = con.ssh.before.decode('utf-8') + con.prompt
            self.connection.log.info(self.result)
        except pexpect.exceptions.TIMEOUT:
            self.connection.log.warning('EnxR CLI failed %s\n\n%s', cmd)
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
