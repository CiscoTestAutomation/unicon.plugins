"""
Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)
"""
import re

from unicon.eal.dialogs import Dialog, Statement
from unicon.bases.routers.connection_provider import BaseStackRpConnectionProvider

from genie.metaparser.util.exceptions import SchemaEmptyParserError

from unicon.plugins.generic.statements import connection_statement_list, custom_auth_statements


class StackwiseVirtualConnectionProvider(BaseStackRpConnectionProvider):
    """ Implements Stack Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to stack device
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the base connection provider
        """
        super().__init__(*args, **kwargs)

    def designate_handles(self):
        """ Identifies the Role of each handle and designates if
          it is active or standby
        """

        con = self.connection

        con.log.info('+++ designating handles for SVL stack +++')

        subcons = list(con._subconnections.items())
        subcon1_alias, subcon1 = subcons[0]
        subcon2_alias, subcon2 = subcons[1]
        target_alias = None
        other_alias = None

        # Try to go to enable mode on both connections
        standby_locked_dialog = Dialog([
            Statement(
                pattern=r'.*Standby console disabled.*',
                action=None,
                loop_continue=False,
                continue_timer=False,
            )
        ])

        for subcon in [subcon1, subcon2]:
            try:
                # Attempt to detect the current state of the subcon and go to enable if not already there
                subcon.state_machine.detect_state(subcon.spawn, subcon.context)
                if subcon.state_machine.current_state != 'enable':
                    subcon.sendline()
                    subcon.state_machine.go_to(
                        'enable',
                        subcon.spawn,
                        context=subcon.context,
                        timeout=con.settings.BOOT_TIMEOUT,
                        dialog=standby_locked_dialog,
                    )
            except Exception as e:
                con.log.exception('Failed to go to enable on %s: %s', subcon.alias, e)
            con.log.debug('{} in state: {}'.format(subcon.alias, subcon.state_machine.current_state))

        if subcon1.state_machine.current_state == 'enable':
            target_con = subcon1
            target_alias = subcon1_alias
            other_alias = subcon2_alias
        elif subcon2.state_machine.current_state == 'enable':
            target_con = subcon2
            target_alias = subcon2_alias
            other_alias = subcon1_alias

        con._set_active_alias(target_alias)
        con._set_standby_alias(other_alias)
        con._handles_designated = True

        device = con.device
        try:
            # To check if the device is in SVL state
            try:
                output = device.parse("show switch")
            except SchemaEmptyParserError:
                con.log.debug("show switch returned empty output")
                output = {}
            stack_info = output.get("switch", {}).get("stack", {})
            roles = [switch_info.get("role") for switch_info in stack_info.values()]
            roles_lower = [str(role).lower() for role in roles if role is not None]

            if "active" in roles_lower and "standby" in roles_lower:
                # Only designate handle when in SVL state
                # There are case when in non-SVL the device connection
                # becomes active for both connection and there isn't a standby state
                # it would have either active and member state or just active state

                # Verify the active and standby
                target_con.spawn.sendline(target_con.spawn.settings.SHOW_REDUNDANCY_CMD)
                output = target_con.spawn.expect(
                    target_con.state_machine.get_state('enable').pattern,
                    timeout=con.settings.EXEC_TIMEOUT).match_output

                state = re.findall(target_con.spawn.settings.REDUNDANCY_STATE_PATTERN, output, flags=re.M)
                target_con.log.debug(f'{target_con.spawn} state: {state}')
                if any('active' in s.lower() for s in state):
                    con._set_active_alias(target_alias)
                    con._set_standby_alias(other_alias)
                elif any('standby' in s.lower() for s in state):
                    con._set_standby_alias(target_alias)
                    con._set_active_alias(other_alias)
                else:
                    raise ConnectionError('unable to designate handles')

        except Exception:
            con.log.exception("Failed to designate handle for SVL stack")

    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device.
            See generic/statements.py for connnection statement lists
        """
        con = self.connection
        custom_auth_stmt = custom_auth_statements(
                             self.connection.settings.LOGIN_PROMPT,
                             self.connection.settings.PASSWORD_PROMPT)
        return con.connect_reply + \
                    Dialog(custom_auth_stmt + connection_statement_list
                        if custom_auth_stmt else connection_statement_list)
