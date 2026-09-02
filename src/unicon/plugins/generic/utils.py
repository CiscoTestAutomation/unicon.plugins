""" Generic utilities. """

from collections.abc import Sequence
import re
import time

from unicon.core.errors import SubCommandFailure
from unicon.utils import Utils, AttributeDict


class GenericUtils(Utils):

    def get_redundancy_details(self, connection, timeout=None, who='my'):
        """
        :arg  connection:  device connection object
        :return: device role and redundancy mode of the device
        """
        timeout = timeout or connection.settings.EXEC_TIMEOUT
        redundancy_details = AttributeDict()
        if who == "peer":
            show_red_out = connection.execute("show redundancy sta |  in peer",
                                              timeout=timeout)
        else:
            show_red_out = connection.execute("show redundancy sta |  in my",
                                              timeout=timeout)

        if re.search("ACTIVE|active", show_red_out):
            redundancy_details['role'] = "active"
            redundancy_details['state'] =\
                show_red_out[show_red_out.find('-') + 1:].strip()
        elif re.search("standby|STANDBY", show_red_out):
            redundancy_details['role'] = "standby"
            redundancy_details['state'] =\
                show_red_out[show_red_out.find('-') + 1:].strip()
        elif re.search("DISABLED|disabled", show_red_out):
            redundancy_details['role'] = "disabled"
            redundancy_details['state'] =\
                show_red_out[show_red_out.find('-') + 1:].strip()
        show_red_out = connection.execute(
            "show redundancy sta | inc Redundancy State")
        redundancy_details['mode'] =\
            show_red_out[show_red_out.find("=") + 1:].strip()
        return redundancy_details

    def is_active_standby_ready(self, connection, timeout=120, interval=30):
        """Check whether active and standby RP are ready using show redundancy.

        Parses 'show redundancy' output to verify:
        - Active RP is in ACTIVE state
        - Standby RP is in STANDBY HOT state

        Args:
            connection: connection object to execute on
            timeout: maximum time to wait in seconds
            interval: polling interval in seconds
        Returns:
            True if both RPs are ready, False on timeout
        """
        start_time = time.time()

          # Current Processor Information :
          # -----------------------
          #   Active Location = slot 6
          #   Current Software state = ACTIVE

        p_active = re.compile(
            r'Current Processor Information[\s\S]*?'
            r'Current Software state\s*=\s*(?P<state>\S+)')
        
        # Peer Processor Information :
        # ----------------------------
        #    Standby Location = slot 7
        #    Current Software state = STANDBY HOT

        p_standby = re.compile(
            r'Peer Processor Information[\s\S]*?'
            r'Current Software state\s*=\s*(?P<state>[\S ]+)')

        while (time.time() - start_time) < timeout:
            try:
                output = connection.execute('show redundancy', timeout=60)
            except Exception as err:
                connection.log.error(
                    'Failed to execute show redundancy: {}'.format(err))
                time.sleep(interval)
                continue

            active_match = p_active.search(output)
            standby_match = p_standby.search(output)

            active_state = active_match.group('state').strip() if active_match else 'Unknown'
            standby_state = standby_match.group('state').strip() if standby_match else 'Unknown'

            connection.log.info(
                'Active RP state: {}, Standby RP state: {}'.format(
                    active_state, standby_state))

            if active_state == 'ACTIVE' and standby_state == 'STANDBY HOT':
                return True

            connection.log.info('Sleeping for {} secs.'.format(interval))
            time.sleep(interval)

        return False

    def flatten_splitlines_command(self, command):
        if isinstance(command, str):
            for item in command.splitlines():
                yield item
        elif isinstance(command, Sequence):
            for item in command:
                yield from self.flatten_splitlines_command(item)
        else:
            raise SubCommandFailure('"command" must be a string'
                                    ' or a list of string')
