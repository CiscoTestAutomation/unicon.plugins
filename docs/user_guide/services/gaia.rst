Check Point Gaia OS
===================

This section lists the services which are supported with the Gaia OS (gaia) Unicon plugin. This plugin is used when `os=gaia` is specified.

  * `execute <#execute>`__
  * `switchto <#switchto>`__
  * `ping <#ping>`__
  * `traceroute <#traceroute>`__

The following generic services are also available:

  * send
  * sendline
  * expect

**Supported CLI states**

The gaia plugin supports two device CLI states: `clish` and `expert`:
The `switchto` service can be used to switch between CLI states. The initial state of the device
is detected on initial connection - both 'expert' and 'clish' are supported as valid device defaults.

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

    >>> response = device.execute('show version all')
    >>> type(response)
    <class 'str'>
    >>> 

    >>> response = device.execute('show version all\nshow arp dynamic all')
    >>> type(response)
    <class 'dict'>
    >>> 

    >>> response = device.execute(['show version all','show arp dynamic all'])
    >>> type(response)
    <class 'dict'>
    >>>


switchto
--------

This service is used to switch to a specific device CLI state. Supported states are:

* `clish`
* `expert`

=============   ======================    =====================================================
Argument        Type                      Description
=============   ======================    =====================================================
target          str                       Target device CLI state
timeout         int (default 60 sec)      (optional) timeout value for the overall interaction.
=============   ======================    =====================================================

Examples:

.. code-block:: python

    >>> device.switchto('expert')
    >>> 
    >>> device.switchto('clish')
    >>> 
