from unicon.plugins.generic.settings import GenericSettings

class NxosSettings(GenericSettings):

    def __init__(self):
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'term length 0',
            'term width 511',
            'terminal session-timeout 0'
        ]
        self.HA_INIT_CONFIG_COMMANDS = [
            'no logging console',
            'line console',
            'exec-timeout 0',
            'line vty',
            'exec-timeout 0',
            'terminal width 511'
        ]
        self.SWITCHOVER_TIMEOUT = 700
        self.SWITCHOVER_COUNTER = 50
        self.HA_RELOAD_TIMEOUT = 700
        self.RELOAD_TIMEOUT = 600
        self.RELOAD_RECONNECT_WAIT = 60
        self.CONSOLE_TIMEOUT = 30
        self.ATTACH_CONSOLE_DISABLE_SLEEP = 250
        self.ERROR_PATTERN = [
            r'^%\s*[Ii]nvalid (command|input|number)',
            r'^%\s*[Ii]ncomplete (command|input)',
            r'^%\s*[Aa]mbiguous (command|input)',
            r'^.*?Overwriting/deleting this image is not allowed',
            r'^.*?Copying to/from this server name is not permitted',
            r'^.*?command failed\.*aborting'
        ]
        self.CONFIGURE_ERROR_PATTERN = [
            r'^%\s*[Ii]nvalid (command|input|number)',
            r'^%\s*[Ii]ncomplete (command|input)',
            r'^%\s*[Cc]an not open.*',
            r'^%\s*[Nn]ot supported.*',
            r'^%\s*[Ff]ail.*',
            r'^%\s*[Aa]bort.*'
            r'^%\s*[Ee](RROR|rror).*',
            r'^%\s*Ambiguous command'
        ]

        self.GUESTSHELL_CONFIG_CMDS = []
        self.GUESTSHELL_CONFIG_VERIFY_CMDS = []
        self.GUESTSHELL_CONFIG_VERIFY_PATTERN = r''
        self.GUESTSHELL_ENABLE_CMDS = 'guestshell enable'
        self.GUESTSHELL_ENABLE_VERIFY_CMDS = 'show guestshell | i State'
        self.GUESTSHELL_ENABLE_VERIFY_PATTERN = r'State\s*:\s*Activated'
