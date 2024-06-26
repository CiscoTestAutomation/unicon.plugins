""" Stack utilities. """

import re
import logging
from time import sleep, time

from unicon.eal.dialogs import Dialog
from unicon.utils import Utils, AttributeDict
from unicon.core.errors import StateMachineError

from .exception import StackMemberReadyException
from .service_statements import send_boot

logger = logging.getLogger(__name__)


class StackUtils(Utils):

    def get_redundancy_details(self, connection, timeout=None):
        """ Get redundancy details from stack device

        Args:
            connection (`obj`): connection object
            timeout (`int`): execute timeout
        Returns:
            redundancy_details (`dict`): redundancy details of all peers
                eg: 
                    {'1': {'mac': 'bcc4.9346.7880',
                        'role': 'Member',
                        'state': 'Ready',
                        'sw_num': '1'},
                    '2': {'mac': 'bcc4.9346.9180',
                        'role': 'Standby',
                        'state': 'Ready',
                        'sw_num': '2'},
                    '3': {'mac': 'bcc4.9346.7280',
                        'role': 'Active',
                        'state': 'Ready',
                        'sw_num': '3'}}
        """
        timeout = timeout or connection.settings.EXEC_TIMEOUT
        redundancy_details = AttributeDict()

        #  1       Member   bcc4.9346.7880     1      V01     Ready
        # *2       Active   bcc4.9346.9180     3      V04     Ready
        #  4       Standby  d8b1.9009.bf80     1      V01     HA sync in progress
        p = re.compile(r'^(\*)?(?P<sw_num>\d+)\s+(?P<role>Member|Active|Standby)\s+'
                       r'(?P<mac>[\w\.]+)\s+\d+\s+\w+\s+(?P<state>[\S\s]+)$')

        output = connection.execute("show switch", timeout=timeout)

        for line in output.splitlines():
            m = p.search(line.strip())
            if m:
                group = m.groupdict()
                redundancy_details.update({group['sw_num']: group})

        return redundancy_details


    def send_boot_cmd(self, connection, timeout, prompt_recovery, dialog=Dialog([])):
        """ Send the boot command when device come to Rommon mode 

        Args:
            connection (`obj`): connection object
            timeout (`int`): execute timeout
            prompt_recovery (`bool`): prompt_recovery flag
            dialog (`Dialog`): dialog to process
        Returns:
            None
        """
        connection.spawn.sendline()
        dialog = dialog + Dialog([send_boot])
        dialog.process(connection.spawn, timeout=timeout,
                        prompt_recovery=prompt_recovery,
                        context=connection.context)


    def boot_process(self, connection, timeout, prompt_recovery, dialog=Dialog([])):
        """ Boot up the device and bring it to disable mode

        Args:
            connection (`obj`): connection object
            timeout (`int`): execute timeout
            prompt_recovery (`bool`): prompt_recovery flag
            dialog (`Dialog`): dialog to process
        Returns:
            None
        """
        connection.spawn.sendline()
        try:
            dialog.process(connection.spawn, timeout=timeout,
                            prompt_recovery=prompt_recovery,
                            context=connection.context)
        except StackMemberReadyException as e:
            logger.debug('This is an expected exception for getting out of the dialog proceess')
            pass
        connection.state_machine.go_to('any', connection.spawn, timeout=timeout,
                                    prompt_recovery=prompt_recovery,
                                    context=connection.context)
        connection.state_machine.go_to('disable', connection.spawn, timeout=timeout,
                                    prompt_recovery=prompt_recovery,
                                    context=connection.context)


    def is_active_standby_ready(self, connection, timeout=120, interval=30):
        """ Check whether active and standby rp are in ready state

        Args:
            connection (`obj`): connection object
            timeout (`int`): timeout value, default is 120 secs
            interval (`int`): check interval, default is 30 secs
        Returns:
            result (`bool`): True if both in ready state, else False
        """
        active = standby = ''
        start_time = time()
        end_time = start_time + timeout

        
        
        while (time() - start_time) < timeout:
            # double check the connection state
            self.wait_for_any_state(connection, timeout=end_time - time(), interval=interval)
            try:
                # one connection reached a known state does not mean all connections are in the same state
                # so cli execution can still fail
                details = self.get_redundancy_details(connection)
            except Exception as e:
                connection.log.warning('Failed to get redundancy details. Stack might not be ready yet')
                connection.log.info('Sleeping for %s secs.' % interval)
                sleep(interval)
                continue

            for sw_num, info in details.items():
                if info['role'] == 'Active':
                    active = info.get('state')
                elif info['role'] == 'Standby':
                    standby = info.get('state')

            if active == 'Ready' and standby == 'Ready':
                return True

            # Not ready sleep and retry
            connection.log.info('Sleeping for %s secs.' % interval)
            sleep(interval)
            continue

        return False


    def is_active_ready(self, connection):
        """ Check whether active rp is in ready state

        Args:
            connection (`obj`): connection object
        Returns:
            result (`bool`): True if in ready state, else False
        """
        active = ''
        details = self.get_redundancy_details(connection)
        for sw_num, info in details.items():
            if info['role'] == 'Active':
                active = info.get('state')

        return active == 'Ready'


    def is_all_member_ready(self, connection, timeout=270, interval=30):
        """ Check whether all rp are in ready state
            including active, standby and members

        Args:
            connection (`obj`): connection object
            timeout (`int`): timeout value, default is 120 secs
            interval (`int`): check interval, default is 30 secs
        Returns:
            result (`bool`): True if all members are in ready state
                             else False
        """
        ready = active = standby = False
        start_time = time()
        end_time = start_time + timeout

        while (time() - start_time) < timeout:
            # double check the console state. 
            self.wait_for_any_state(connection, timeout=end_time - time(), interval=interval)
            try:
                # one connection reached a known state does not mean all connections are in the same state
                # so cli execution can still fail
                details = self.get_redundancy_details(connection)
            except Exception as e:
                connection.log.warning('Failed to get redundancy details. Stack might not be ready yet')
                connection.log.info('Sleeping for %s secs.' % interval)
                sleep(interval)
                continue
            for sw_num, info in details.items():
                state = info.get('state')
                if state != 'Ready':
                    ready = False
                    break
                if info['role'] == 'Active':
                    active = True
                if info['role'] == 'Standby':
                    standby = True
            else:
                ready = True

            if ready and active and standby:
                return True
            # Not ready sleep and retry
            connection.log.info('Sleeping for %s secs.' % interval)
            sleep(interval)
            continue

        return False


    def get_standby_rp_sn(self, connection):
        """ Get the standby rp switch number

        Args:
            connection (`obj`): connection object
        Returns:
            standby (`int`): switch number for standby
        """
        standby = None
        details = self.get_redundancy_details(connection)
        for sw_num, info in details.items():
            role = info.get('role')
            if role == 'Standby':
                standby = int(sw_num)

        return standby
    
    
    def wait_for_any_state(self, connection, timeout=180, interval=15, auto_timeout_extend=True, auto_extend_secs=180):
        ''' use this method to wait for any state or bypass possible timing issue which could cause state detection failure
            use this where false failure is seen due to timing issue
            Args:
                connection (`obj`): connection object
                timeout (`int`): timeout value, default is 180 secs
                interval (`int`): check interval, default is 15 secs
                auto_timeout_extend (`bool`): auto extend timeout if less than 0
                                              This is useful when the timeout is calculated based on an estimated total timeout
                auto_extend_secs (`int`): Extend timeout to this vaule when auto_timeout_extend is True. Default is 180 secs
            Returns:
                None
                raises StateMachineError if state detection fails and timeout is reached

        '''
        start_time = time()
        good_state = False
        if timeout <= 0 and auto_timeout_extend:
            connection.log.warning(f'wait_for_any_state: given timeout is less than 0. Extend it to {auto_extend_secs} seconds')
            timeout = auto_extend_secs
        elif timeout <= 0:
            connection.log.warning(f'wait_for_any_state: given timeout is less than 0. No auto extend. set timeout to 10 seconds')
            timeout = 10 # set it to 10 seconds to check at least once
        else:
            connection.log.warning(f'wait_for_any_state: given timeout={timeout} seconds. No auto extend')
            
        connection.log.info(f'Looking for known state (detect_state) on {connection.alias} -- timeout={timeout} seconds')
        while (time() - start_time) < timeout:
            t_left = timeout - (time() - start_time)
            connection.log.info('-- checking time left: %0.1f secs' % t_left)
            try:
                connection.state_machine.detect_state(connection.spawn, context=connection.context)
                good_state = True
                break
            except Exception as e:
                connection.log.warning(f'Fail to detect any state on {connection.alias}')
                connection.log.info(f'Sleep {interval} secs')
                sleep(interval)
        if not good_state:
            raise StateMachineError(f'wait_for_any_state: Timeout reached on {connection.alias}')
        else:
            connection.log.info(f'detect_state on {connection.alias} is successful')
