
from unicon.bases.routers.services import BaseService
from unicon.plugins.generic.service_implementation import ReloadResult
from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.utils import AttributeDict

from .service_statements import reload_statement_list


class Reload(BaseService):
    """Service to reload the device.

    Arguments:
        reload_command: reload command to be issued on device.
            default reload_command is "reload"
        dialog: Dialog which include list of Statements for
            additional dialogs prompted by reload command, in-case
            it is not in the current list.
        timeout: Timeout value in sec, Default Value is 400 sec
        image_to_boot: image to be used if the device stops in rommon mode

    Returns:
        bool: True on success False otherwise

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            uut.reload()
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.dialog = Dialog(reload_statement_list)

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     timeout=None,
                     return_output=False,
                     error_pattern=None,
                     append_error_pattern=None,
                     *args,
                     **kwargs):

        con = self.connection
        timeout = timeout or self.timeout

        if error_pattern is None:
            self.error_pattern = con.settings.ERROR_PATTERN
        else:
            self.error_pattern = error_pattern

        if not isinstance(self.error_pattern, list):
            raise ValueError('error_pattern should be a list')
        if append_error_pattern:
            if not isinstance(append_error_pattern, list):
                raise ValueError('append_error_pattern should be a list')
            self.error_pattern += append_error_pattern
        sm = self.get_sm()
        assert isinstance(dialog,
                          Dialog), "dialog passed must be an instance of Dialog"
        dialog += self.dialog

        con.log.debug(
            "+++ reloading  {}  with reload_command {} and timeout is {} +++"
            .format(self.connection.hostname, reload_command, timeout))

        context = AttributeDict(self.context)
        dialog = self.service_dialog(service_dialog=dialog)
        dialog += Dialog([[sm.get_state('disable').pattern]])
        con.spawn.sendline(reload_command)
        try:
            reload_op=dialog.process(con.spawn, context=context, timeout=timeout,
                                     prompt_recovery=self.prompt_recovery)
            sm.detect_state(con.spawn, context=context)
            con.state_machine.go_to('enable', con.spawn,
                                    context=context,
                                    timeout=con.connection_timeout,
                                    prompt_recovery=self.prompt_recovery)
        except Exception as err:
            raise SubCommandFailure("Reload failed : {}".format(err))

        con.log.debug("+++ Reload Completed Successfully +++")
        self.result = True
        if return_output:
            self.result = ReloadResult(self.result, reload_op.match_output.replace(reload_command, '', 1))
