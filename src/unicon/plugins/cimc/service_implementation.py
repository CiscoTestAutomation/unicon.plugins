__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.eal.dialogs import Dialog

from unicon.plugins.generic.service_implementation import Execute as GenericExecute

from .statements import CimcStatements


statements = CimcStatements()


class Execute(GenericExecute):
    """ Execute Service implementation

    Service  to executes exec_commands on the device and return the
    console output. reply option can be passed for the interactive exec
    command.

    Arguments:
        command: exec command
        reply: Additional Dialog patterns for interactive exec commands.
        timeout : Timeout value in sec, Default Value is 60 sec

    Returns:
        True on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:: python

              output = dev.execute("show command")

    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog([statements.enter_yes_or_no_stmt])


