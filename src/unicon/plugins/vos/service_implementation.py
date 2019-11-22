__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import re

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog, Statement

from unicon.plugins.generic.service_implementation import Execute as GenericExecute
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.vos.patterns import VosPatterns
from unicon.plugins.generic import GenericUtils
from .statements import VosStatements


statements = VosStatements()
p = VosPatterns()
utils = GenericUtils()


class Execute(GenericExecute):
    """ Execute Service implementation

    Service  to executes exec_commands on the device and return the
    console output. reply option can be passed for the interactive exec
    command.

    Arguments:
        command: exec command
        reply: Additional Dialog patterns for interactive exec commands.
        timeout : Timeout value in sec, Default Value is 60 sec
        lines: number of lines to capture when paging is active. Default: 100

    Returns:
        True on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:: python

              output = dev.execute("show command")

    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog([statements.continue_stmt])

    def extra_output_process(self, output):
        return utils.remove_backspace(output)

    def post_service(self, *args, **kwargs):

        def clean_output(output):
            # Remove 'Press enter..' prompts. Using [1:] to remove the ^ character from the pattern.
            output = re.sub(p.press_enter_space_q[1:] + r'\r?\x1b\[K', '', output)
            # Remove 'options: ..' prompts. Using [1:] to remove the ^ character from the pattern.
            output = re.sub(p.paging_options[1:] + '\r\n', '', output)
            return output

        if isinstance(self.result, str):
            self.result = clean_output(self.result)
        elif isinstance(self.result, list):
            for x,command in enumerate(self.result):
                if isinstance(command, str):
                    self.result[x] = clean_output(command)
        elif isinstance(self.result, dict):
            for cmd in self.result:
                if isinstance(self.result[cmd], str):
                    self.result[cmd] = clean_output(self.result[cmd])
                elif isinstance(self.result[cmd], list):
                    for x,command in enumerate(self.result[cmd]):
                        if isinstance(command, str):
                            self.result[cmd][x] = clean_output(command)

