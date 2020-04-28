__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "dwapstra"

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog, Statement

from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic.service_implementation import Execute as GenericExecute
from unicon.plugins.windows.patterns import WindowsPatterns

from unicon.plugins.generic import GenericUtils

utils = GenericUtils()


class Execute(GenericExecute):
    """ Execute Service implementation

    Service  to executes exec_commands on the device and return the
    console output. reply option can be passed for the interactive exec
    command.

    Arguments:
        command: (str) exec command
        reply: (Dialog) Additional Dialog patterns for interactive exec commands.
        timeout: (int) Timeout value in sec, Default Value is 60 sec

    Returns:
        True on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:: python

              output = dev.execute("show command")

    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.service_name = 'execute'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.__dict__.update(kwargs)

