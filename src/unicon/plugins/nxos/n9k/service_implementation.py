__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.eal.dialogs import Dialog
from unicon.plugins.nxos.service_implementation import Reload, \
    HANxosReloadService

from .service_statements import loader


class Nxos9kReload(Reload):
    """ Service to reload the device.

    Arguments:
        reload_command: reload command to be issued on device.
            default reload_command is "reload"
        dialog: Dialog which include list of Statements for
            additional dialogs prompted by reload command, in-case
            it is not in the current list.
        timeout: Timeout value in sec, Default Value is 400 sec
        return_output: if True, return namedtuple with result and reload output
        config_lock_retries: retry times if config mode is locked, default is 20
        config_lock_retry_sleep: sleep between retries, default is 9 sec
        image_to_boot: image name for boot if device goes into loader state

    Returns:
        bool: True on success False otherwise

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            rtr.reload()
            # If reload command is other than 'reload'
            rtr.reload(reload_command="reload location all", timeout=400)
    """

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     timeout=None,
                     return_output=False,
                     config_lock_retries=None,
                     config_lock_retry_sleep=None,
                     image_to_boot='',
                     *args,
                     **kwargs):
        if image_to_boot:
            self.context['image_to_boot'] = image_to_boot
        try:
            super().call_service(
                reload_command=reload_command,
                dialog=Dialog([loader]) + dialog,
                timeout=timeout,
                return_output=return_output,
                config_lock_retries=config_lock_retries,
                config_lock_retry_sleep=config_lock_retry_sleep,
                *args,
                **kwargs
            )
        finally:
            if image_to_boot:
                self.context.pop('image_to_boot')


class HANxos9kReloadService(HANxosReloadService):
    """ Service to reload the device.

    Arguments:
        reload_command : reload command to be issued on device.
        default reload_command is "reload"

        dialog : Dialog which include list of Statements for
                additional dialogs prompted by reload command, in-case
                it is not in the current list.

        timeout : Timeout value in sec, Default Value is 600 sec
        return_output: if True, return namedtuple with result and reload output
        config_lock_retries: retry times if config mode is locked, default is 20
        config_lock_retry_sleep: sleep between retries, default is 9 sec
        image_to_boot: image name for boot if device goes into loader state

    Returns:
        bool: True on success False otherwise

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

              rtr.reload()
              # If reload command is other than 'reload'
              rtr.reload(reload_command="reload location all", timeout=700)
    """

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     target='active',
                     timeout=None,
                     return_output=False,
                     config_lock_retries=None,
                     config_lock_retry_sleep=None,
                     image_to_boot='',
                     *args,
                     **kwargs):
        if image_to_boot:
            self.context['image_to_boot'] = image_to_boot
        try:
            super().call_service(
                reload_command=reload_command,
                dialog=Dialog([loader]) + dialog,
                target=target,
                timeout=timeout,
                return_output=return_output,
                config_lock_retries=config_lock_retries,
                config_lock_retry_sleep=config_lock_retry_sleep,
                *args,
                **kwargs
            )
        finally:
            if image_to_boot:
                self.context.pop('image_to_boot')
