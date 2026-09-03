__author__ = 'Difu Hu <difhu@cisco.com>'

import time
from unicon.eal.dialogs import Dialog
from unicon.plugins.nxos.service_implementation import Reload, \
    HANxosReloadService, AttachModuleConsole

from .service_statements import loader
from unicon.core.errors import SubCommandFailure, TimeoutError

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


class AttachModuleConsoleN9k(AttachModuleConsole):
    """ Service to attach to N9K module console (linecard) via rlogin.
    This service provides a context manager to connect to a linecard console
    on Nexus 9000 devices using the 'run bash sudo rlogin lc<N>' command.

    The service returns a context manager that:
    - Attaches to the specified module console on entry
    - Automatically detaches and returns to enable state on exit
    - Provides execute() method for running commands on the module

    Example:
        .. code-block:: python
            # Attach to module 1 console and run commands
            with device.attach_console(module_num=1) as console:
                output = console.execute('show version')
                console.execute('reload')
    """

    def __init__(self, *args, **kwargs):
        """Initialize the attach console service.
        Sets the start and end states to 'enable' to ensure the device
        is in the correct state before and after console attachment.
        """
        super().__init__(*args, **kwargs)
        self.start_state = "enable"
        self.end_state = "enable"

    def call_service(self, module_num, **kwargs):
        """Create and return a context manager for module console attachment.
        Args:
            module_num (int): Module/linecard number to attach to (e.g., 1 for lc1)
            **kwargs: Additional arguments passed to ContextMgr
                timeout (int, optional): Console operation timeout in seconds
                max_retries (int, optional): Maximum retry attempts (default: 2)
        Returns:
            ContextMgr: Context manager object for console operations
        """
        self.result = self.__class__.ContextMgr(connection=self.connection,
                                                module_num=module_num,
                                                **kwargs)

    class ContextMgr(object):
        """Context manager for N9K module console operations.
        Handles the connection lifecycle to a module console:
        - Establishes rlogin connection on entry (__enter__)
        - Executes commands on the module console
        - Gracefully disconnects on exit (__exit__)
        """

        def __init__(self,
                     connection,
                     module_num,
                     timeout=None,
                     max_retries=2):
            """Initialize context manager for module console.
            Args:
                connection: Device connection object
                module_num (int): Module/linecard number (1-based)
                timeout (int, optional): Operation timeout, defaults to CONSOLE_TIMEOUT setting
                max_retries (int, optional): Maximum connection retry attempts (default: 2)
            """
            self.conn = connection
            self.module_num = module_num
            self.timeout = timeout or connection.settings.CONSOLE_TIMEOUT
            self.max_retries = max_retries

        def __enter__(self):
            """Enter the module console context.
            Executes 'run bash sudo rlogin lc<N>' to attach to the module console
            and waits for the module prompt to appear.
            Returns:
                self: Context manager instance for command execution
            Raises:
                TimeoutError: If module prompt is not seen within timeout
                SubCommandFailure: If console attachment fails
            """
            self.conn.log.debug('+++ attaching console +++')
            try:
                # Execute the rlogin command to attach to module console
                self.conn.log.debug('Sending: run bash sudo rlogin lc%s' % (self.module_num))
                self.conn.sendline('run bash sudo rlogin lc%s' % self.module_num)

                # Wait for bash prompt (e.g., root@lc1:~#)
                patterns = [
                    r'root@lc\d+:~#',           # Bash prompt for root user on linecard
                    r'root@lc\d+:\S+#',         # Bash prompt with different working directory
                ]
                match_output = self.conn.expect(patterns, timeout=self.timeout)

                # Get the matched output - use match object instead of buffer
                if hasattr(match_output, 'match_output'):
                    output = match_output.match_output
                elif hasattr(self.conn.spawn, 'match'):
                    output = self.conn.spawn.match.string if self.conn.spawn.match else ''
                else:
                    output = self.conn.spawn.before + self.conn.spawn.after

                self.conn.log.debug('Module console output: %s' % output)
                self.conn.log.debug('Successfully attached to module-%s console' % self.module_num)
                return self
            except Exception as e:
                self.conn.log.error('Failed to attach to module-%s console: %s' %
                                    (self.module_num, str(e)))
                raise

        def __exit__(self, exc_type, exc_value, exc_tb):
            """Exit the module console context and return to enable state.
            Sends 'exit' to close the rlogin connection and waits for the
            device to return to the switch enable prompt.
            Args:
                exc_type: Exception type if an exception occurred
                exc_value: Exception value if an exception occurred
                exc_tb: Exception traceback if an exception occurred
            Returns:
                False: Always returns False to propagate exceptions
            """
            self.conn.log.debug('--- detaching console ---')
            try:
                # Send exit to leave the module console (rlogin session)
                self.conn.sendline('exit')
                
                # Wait for the rlogin connection closed confirmation message
                try:
                    self.conn.expect([r'rlogin: Connection to lc\d+ closed normally'], timeout=10)
                    self.conn.log.debug('Rlogin connection closed')
                except TimeoutError:
                    self.conn.log.warning('Did not see rlogin closed message')
                
                # Wait for the switch enable prompt to confirm we're back
                patterns = [r'\S+#\s*$']
                try:
                    self.conn.expect(patterns, timeout=10)
                except TimeoutError:
                    self.conn.log.warning('Timeout waiting for switch prompt after exit')
                    # Try to recover by sending a newline
                    self.conn.sendline('')
                    
            except Exception as e:
                self.conn.log.error('Error while detaching from console: %s' % str(e))
                try:
                    [self.conn.sendline(cmd) for cmd in ('exit', '')]
                except:
                    pass
            return False

        def execute(self, command, timeout=None):
            """Execute a command on the module console.
            Sends a command to the module console, waits for the prompt,
            and returns the command output with echo removed.
            Args:
                command (str): Command to execute on the module
                timeout (int, optional): Command timeout in seconds,
                    defaults to the console timeout setting
            Returns:
                str: Command output (stripped, with command echo removed)
            Raises:
                TimeoutError: If the module prompt is not seen within timeout
            Example:
                >>> with device.attach_console(module_num=1) as console:
                ...     output = console.execute('show version')
            """
            timeout = timeout or self.timeout

            # Send the command to the module console
            self.conn.sendline(command)
            
            # Wait for the bash prompt to return (since we use sudo rlogin)
            patterns = [
                r'root@lc\d+:~#',           # Bash prompt for root user on linecard
                r'root@lc\d+:\S+#',         # Bash prompt with different working directory
            ]

            try:
                self.conn.expect(patterns, timeout=timeout)

                # Extract output from before the prompt
                output = self.conn.spawn.before if hasattr(self.conn.spawn, 'before') else ''

                if output:
                    lines = output.split('\r\n')
                    # Remove the command echo (first line typically echoes the command)
                    if lines and lines[0].strip() == command.strip():
                        output = '\r\n'.join(lines[1:])
                    elif lines and command.strip() in lines[0]:
                        output = '\r\n'.join(lines[1:])

                return output.strip() if output else ''
            except TimeoutError as e:
                self.conn.log.error('Timeout executing command: %s' % command)
                raise

        def __getattr__(self, attr):
            """Delegate specific connection methods to the underlying connection object.
            Allows direct access to sendline, expect, and send methods
            from the console context manager for advanced usage.
            Args:
                attr (str): Attribute name being accessed
            Returns:
                method: The requested method from the connection object
            Raises:
                AttributeError: If the attribute is not one of the delegated methods
            """
            # Delegate these low-level connection methods to the underlying connection
            if attr in ('sendline', 'expect', 'send'):
                return getattr(self.conn, attr)

            raise AttributeError('%s object has no attribute %s'
                                 % (self.__class__.__name__, attr))