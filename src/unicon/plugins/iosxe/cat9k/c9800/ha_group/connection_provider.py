"""Connection provider for a C9800 HA group."""

import re

from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.connection_provider import (
    GenericDualRpConnectionProvider,
)


REDUNDANCY_ROLE_RE = re.compile(
    r'^\s*(?:my|peer) state\s*=.*?-\s*(?P<role>ACTIVE|STANDBY)\b',
    re.I | re.M,
)


class IosXEc9800HAGroupConnectionProvider(
        GenericDualRpConnectionProvider):
    """Connection provider for paired or standalone C9800 members."""

    def learn_hostname(self, subconnection):
        """Retain the hostname learned by each individual group member."""
        learned_hostname = subconnection._get_learned_hostname(
            subconnection.spawn)
        if (
            subconnection.learn_hostname
            and not subconnection.learned_hostname
            and subconnection.state_machine.current_state != 'shell'
            and learned_hostname !=
                subconnection.settings.DEFAULT_LEARNED_HOSTNAME
        ):
            subconnection.log.info(
                "Learned hostname(s): '%s'.", learned_hostname)
            # The parent HA-group name is not a CLI hostname. Store the
            # learned name only on the member that produced the prompt.
            subconnection.learned_hostname = learned_hostname
            return

        super().learn_hostname(subconnection)

    def designate_handles(self):
        """Designate active and standby handles for the C9800 group."""
        con = self.connection

        con.log.info('+++ designating handles for C9800 HA group +++')

        subcons = list(con._subconnections.items())
        subcon1_alias, subcon1 = subcons[0]
        subcon2_alias, subcon2 = subcons[1]
        target_alias = None
        other_alias = None

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
                subcon.state_machine.detect_state(
                    subcon.spawn, subcon.context)
                if subcon.state_machine.current_state != 'enable':
                    subcon.sendline()
                    subcon.state_machine.go_to(
                        'enable',
                        subcon.spawn,
                        context=subcon.context,
                        timeout=con.settings.BOOT_TIMEOUT,
                        dialog=standby_locked_dialog,
                    )
            except Exception as error:
                con.log.exception(
                    'Failed to go to enable on %s: %s',
                    subcon.alias,
                    error,
                )
            con.log.debug(
                '%s in state: %s',
                subcon.alias,
                subcon.state_machine.current_state,
            )

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
            redundancy_output = device.execute(
                'show redundancy state',
                matched_retries=(
                    con.settings.EXECUTE_MATCHED_RETRIES
                ),
                matched_retry_sleep=(
                    con.settings.EXECUTE_MATCHED_RETRY_SLEEP
                ),
            )
            roles_lower = [
                match.group('role').lower()
                for match in REDUNDANCY_ROLE_RE.finditer(
                    redundancy_output or '')
            ]

            if 'active' in roles_lower and 'standby' in roles_lower:
                target_con.spawn.sendline(
                    target_con.spawn.settings.SHOW_REDUNDANCY_CMD)
                output = target_con.spawn.expect(
                    target_con.state_machine.get_state('enable').pattern,
                    timeout=con.settings.EXEC_TIMEOUT,
                ).match_output

                state = re.findall(
                    target_con.spawn.settings.REDUNDANCY_STATE_PATTERN,
                    output,
                    flags=re.M,
                )
                target_con.log.debug(
                    '%s state: %s', target_con.spawn, state)
                if any('active' in value.lower() for value in state):
                    con._set_active_alias(target_alias)
                    con._set_standby_alias(other_alias)
                elif any('standby' in value.lower() for value in state):
                    con._set_standby_alias(target_alias)
                    con._set_active_alias(other_alias)
                else:
                    raise ConnectionError('unable to designate handles')

        except Exception:
            con.log.exception(
                'Failed to designate handles for C9800 HA group')
