""" Stack IOS-XE Settings. """

from unicon.plugins.iosxe.settings import IosXESettings

class IosXEStackSettings(IosXESettings):

    def __init__(self):
        super().__init__()

        # Switchover service timeout
        self.STACK_SWITCHOVER_TIMEOUT = 600
        # Switchover postcheck interval
        self.SWITCHOVER_POSTCHECK_INTERVAL = 30
        self.POST_SWITCHOVER_SLEEP = 90

        # Secs to sleep before reconnect device
        self.STACK_POST_RELOAD_SLEEP = 30
        # Secs to sleep before booting device
        self.STACK_ROMMON_SLEEP = 20
        # Stack reload timeout
        self.STACK_RELOAD_TIMEOUT = 900
        # Reload postcheck interval
        self.RELOAD_POSTCHECK_INTERVAL = 30
        # Timeout for boot
        self.STACK_BOOT_TIMEOUT = 1000

        self.CONFIGURE_ALLOW_STATE_CHANGE = True
        
        # Secs to sleep after booting the device
        self.STACK_ENABLE_SLEEP = 100

        # Some stack topologies expose only the active RP's console (all
        # terminal-server lines land on the active). In that case the
        # designated standby handle is really another session on the active,
        # so device.standby / target='standby' / swap_roles() cannot reach the
        # standby RP.
        #
        # When enabled, init_standby() detects that situation and descends into
        # the standby RP console using:
        #     request platform software console attach switch standby <plane>
        # After that the standby handle is a genuine standby session and all
        # existing services behave normally.
        #
        # Off by default: it costs a 'show switch' on every console and an
        # attach attempt on any stack where no console is on the standby, so it
        # is opted into per testbed rather than changing every stack connect.
        self.STACK_STANDBY_CONSOLE_ATTACH = False
        # Route-processor plane used by the console attach command
        self.STACK_STANDBY_CONSOLE_PLANE = 'R0'
        # Timeout for the console attach + login sequence
        self.STACK_STANDBY_CONSOLE_ATTACH_TIMEOUT = 120
        # How often to poke the attached console while waiting for its prompt
        self.STACK_STANDBY_CONSOLE_POLL_INTERVAL = 20
        # The standby RP console is heavily rate limited, so large outputs
        # stall part way through and time out the connect. These init commands
        # are skipped on an attached standby console; the active handle has
        # already supplied the same information.
        self.STACK_STANDBY_CONSOLE_SKIP_INIT_COMMANDS = ['show version']