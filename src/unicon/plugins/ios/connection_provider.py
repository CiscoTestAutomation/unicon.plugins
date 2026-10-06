import re

from unicon.plugins.generic.connection_provider import (
    GenericDualRpConnectionProvider,
    GenericSingleRpConnectionProvider,
)


def update_ios_os_version(con):
    device = con.device

    if not device:
        return

    try:
        alias_n = 0
        if (match := re.search(r'-(\d+)$', con.alias or '')):
            alias_n = int(match.group(1))
        if match is None or alias_n == 1:
            execute_output = con.execute('show version')
            parsed_output = device.parse(
                'show version', output=execute_output)
            version = parsed_output.get('version', {}).get('version')
            if version:
                device.version = version
    except Exception:
        con.log.error('Could not learn the os version')


def remove_show_version_init_command(con):
    """Remove the default show version command before learning the version."""
    if con.init_exec_commands is None:
        con.settings.HA_INIT_EXEC_COMMANDS = [
            command for command in con.settings.HA_INIT_EXEC_COMMANDS
            if command != 'show version'
        ]


class IosSingleRpConnectionProvider(GenericSingleRpConnectionProvider):
    """IOS single-RP connection provider."""

    def update_os_version(self):
        update_ios_os_version(self.connection)

    def init_connection(self):
        if self.connection.learn_os_version:
            remove_show_version_init_command(self.connection)

        super().init_connection()

        if self.connection.learn_os_version:
            self.update_os_version()


class IosDualRpConnectionProvider(GenericDualRpConnectionProvider):
    """IOS dual-RP connection provider."""

    def update_os_version(self):
        update_ios_os_version(self.connection)

    def init_connection(self):
        if self.connection.learn_os_version:
            remove_show_version_init_command(self.connection)

        super().init_connection()

        if self.connection.learn_os_version:
            self.update_os_version()
