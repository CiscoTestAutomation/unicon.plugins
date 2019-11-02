import os
import re

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog

from .patterns import (AireosPatterns, AireosReloadPatterns,
    AireosPingPatterns, AireosCopyPatterns)

from .service_statements import reload_statements

pr = AireosReloadPatterns()
pp = AireosPingPatterns()
pc = AireosCopyPatterns()
p = AireosPatterns()


class AireosReload(BaseService):

    def __init__(self, connection, context, **kwargs):
        self.connection = connection
        self.context = context
        self.timeout_pattern = ['Timeout occurred', ]
        self.error_pattern = [r'Invalid', r'Incorrect', r'HELP']
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.service_name = 'reload'
        self.timeout = self.connection.settings.RELOAD_TIMEOUT
        self.dialog_reload = Dialog(reload_statements)
        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self,
                     reload_command='reset system forced',
                     dialog=Dialog([]),
                     timeout=None,
                     **kwargs):
        con = self.connection
        timeout = timeout or self.timeout
        con.log.debug('+++ reloading  %s  with reload_command %s and timeout is %s +++'
                      % (self.connection.hostname, reload_command, timeout))

        dialog += self.dialog_reload
        try:
            con.spawn.sendline(reload_command)
            self.result = dialog.process(con.spawn,
                                         timeout=timeout,
                                         prompt_recovery=self.prompt_recovery)
            con.state_machine.go_to('any',
                                    con.spawn,
                                    context=self.context,
                                    prompt_recovery=self.prompt_recovery,
                                    timeout=con.connection_timeout,
                                    dialog=con.connection_provider.get_connection_dialog())
            con.connection_provider.init_handle()
        except Exception as err:
            raise SubCommandFailure('Reload failed %s' % err)


class AireosPing(BaseService):

    def __init__(self, connection, context, **kwargs):
        self.connection = connection
        self.context = context
        self.timeout_pattern = ['Timeout occurred', ]
        self.error_pattern = [r'Invalid', r'Incorrect', r'HELP']
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.service_name = 'ping'
        self.timeout = 60

        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, *args, **kwargs):
        con = self.connection
        timeout = self.timeout

        addr = kwargs['addr']
        if addr == '':
            if args[0]:
                addr = args[0]
            else:
                raise SubCommandFailure('Address is not specified ')

        cmd = 'ping ' + addr
        con.spawn.sendline(cmd)

        # It seems we also want to return the command sent
        # con.spawn.expect([cmd])

        try:
            # Wait for prompt
            state = con.state_machine.get_state('enable')
            self.result = con.spawn.expect(state.pattern, timeout=timeout).match_output
        except Exception:
            raise SubCommandFailure('Ping failed')
        m = re.search(pp.bad_ping, self.result)
        if m is None:
            m = re.search(pp.incorrect_ping, self.result)
        if m is not None:
            raise SubCommandFailure('Ping failed')

        if self.result.rfind(self.connection.hostname):
            self.result = self.result[:self.result.rfind(self.connection.hostname)].strip()


class AireosCopy(BaseService):
    def __init__(self, connection, context, **kwargs):
        self.connection = connection
        self.context = context
        self.timeout_pattern = ['Timeout occurred', ]
        self.error_pattern = []
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.service_name = 'copy'
        self.dialog = Dialog([
            [pr.are_you_sure,
                lambda spawn: spawn.sendline('y'),
                None, True, False],
            [pc.tftp_starting,
                None, None, True, False],
            [pc.tftp_complete,
                None, None, True, False],
            [pc.restart_system,
                None, None, False, False],
            # Sometime, when AP Images are missing TSIM needs a little prod
            [pc.reboot_to_complete,
                lambda spawn: spawn.sendline('reset system forced'),
                None, True, False]])

        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, timeout=None, *args, **kwargs):
        con = self.connection

        if 'config' in kwargs:
            prompt = p.shell

            con.spawn.sendline('devshell shell')
            con.spawn.expect([prompt])
            con.spawn.sendline('cat <<END_OF_FILE >sim.txt')
            con.spawn.sendline(kwargs['config'])
            con.spawn.sendline('END_OF_FILE')
            con.spawn.expect([prompt])
            con.execute('exit')

            # Save conf file
            con.sendline('save config')
            con.spawn.expect([pc.are_you_sure_save])
            con.execute('y')
            con.reload()
            self.result = ""
            return

        # Default values
        param = {
            'mode': 'code',
            'source_file': '',
            'source': '',
            'server': ''
        }

        # Read input values passed
        for key in kwargs:
            param[key] = kwargs[key]

        # Extract directory and filename
        if len(param['source_file']) is '':
            raise SubCommandFailure('Source file must be specified')
        param['path'] = os.path.dirname(param['source_file'])
        param['source_file'] = os.path.basename(param['source_file'])

        # Validate input
        if param['source_file'] is '':
            raise SubCommandFailure('Source file must be specified')
        if param['path'] is '':
            raise SubCommandFailure('Server path must be specified')
        if param['server'] is '':
            raise SubCommandFailure('Server address must be specified for remote copy')

        # Sets the time it takes to download and trigger reboot
        if param['mode'] is 'code':
            timeout = 200
        elif param['mode'] is 'simconfig':
            timeout = 50
        else:
            raise SubCommandFailure('Copy mode must be \'code\' or \'simconfig\'')

        try:
            ret = ''
            ret += con.execute('transfer download datatype ' + param['mode']) + '\n'
            ret += con.execute('transfer download mode tftp') + '\n'
            ret += con.execute('transfer download serverip ' + param['server']) + '\n'
            ret += con.execute('transfer download path ' + param['path']) + '\n'
            ret += con.execute('transfer download filename ' + param['source_file'])
            self.result = ret.strip()
            con.reload(reload_command='transfer download start',
                       timeout=timeout,
                       dialog=self.dialog)
        except Exception as err:
            raise SubCommandFailure("Copy failed", err)
