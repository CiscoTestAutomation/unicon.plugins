FXOS
====

This section lists the services which are supported with Firepower Extensible Operating System (FXOS) Unicon plugin.

  * `execute <#execute>`__

The following generic services are also available:

  * send
  * sendline
  * expect
  * log_user


execute
-------

This service is used to execute arbitrary commands on the device. It is
intended to execute non-interactive commands. In case you want to execute
an command that uses interactive responses use `reply` option to specify 
the Dialog object that handles the responses.

=============   ======================    =====================================================
Argument        Type                      Description
=============   ======================    =====================================================
command         str, list                 command(s) to execute
timeout         int (default 60 sec)      (optional) timeout value for the overall interaction.
reply           Dialog                    (optional) additional dialog object
=============   ======================    =====================================================

The `execute` service returns the output of the command in string format if a single command
is passed. If multiple commands are passed, the returned data is a dictionary with the commands
as keys and the responses as values. You can expect a TimeoutError, StateMachineError or 
SubCommandFailure error in case anything goes wrong.

The commands to execute can be specified as a single command, a newline separated list of 
commands or a list of commands.

.. code-block:: python

    >>> response = device.execute('show version')
    >>> type(response)
    <class 'str'>
    >>> 

    >>> response = device.execute('show version\nshow arp')
    >>> type(response)
    <class 'dict'>
    >>> 

    >>> response = device.execute(['show version','show arp'])
    >>> type(response)
    <class 'dict'>
    >>>



