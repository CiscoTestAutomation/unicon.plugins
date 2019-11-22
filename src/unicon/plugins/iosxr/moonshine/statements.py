from unicon.plugins.iosxr.statements import IOSXRStatements
from unicon.plugins.iosxr.moonshine.patterns import MoonshinePatterns
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.helpers import sendline
import time

patterns = MoonshinePatterns()

def shell_handler(spawn, context, session):
    """ handles Moonshine shell prompt
    """
    print("In shell_handler, sending line exec")
    spawn.sendline('exec')


class MoonshineStatements(IOSXRStatements):
    def __init__(self):
        super().__init__()
        self.shell_stmt = Statement(pattern=patterns.shell_prompt,
                                       action=shell_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)
