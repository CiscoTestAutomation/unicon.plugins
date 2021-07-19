ConfD
=====

This section lists the services which are supported with ConfD based CLI. This plugin
can be used with NSO, CSP, ESC and NFVIS. For the CSP, ESC and NFVIS plugins, specify the
platform as `csp`, `esc` or `nfvis` respectively.

  * `execute <#execute>`__
  * `configure <#configure>`__
  * `cli_style <#cli-style>`__ (ConfD only)
  * `command <#command>`__
  * `reload <#reload>`__ (CSP only)

The following generic services are also available:

  * `send <generic_services.html#send>`__
  * `sendline <generic_services.html#sendline>`__
  * `expect <generic_services.html#expect>`__
  * `log_user <generic_services.html#log-user>`__


**Chatty terminal ignore**

It is currently not possible to disable terminal logging like in IOS. To enable the ConfD plugin
to ignore 'chatty terminal' output, set the ``IGNORE_CHATTY_TERM_OUTPUT`` boolean setting for
the connection to ``True``.

.. code-block:: python

        dev.connect()
        dev.settings.IGNORE_CHATTY_TERM_OUTPUT = True
        dev.execute('cmd')


**Error pattern handling**

If you want to execute commands that could fail to execute properly and you want to verify
this automatically using a specific error pattern, you can specify the `error_pattern`
option with a list of regular expressions to match on the output. This option is available
for the execute, configure, and command service.

.. code-block:: python

    >>> c.execute('show command error', error_pattern=['----\^'])

    2017-07-20T09:47:34: %UNICON-INFO: +++ execute  +++

    2017-07-20T09:47:34: %UNICON-INFO: +++ command  +++
    show command error
    -----------------------------^
    syntax error: unknown argument
    user@ncs> Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/projects/unicon/src/unicon/bases/routers/services.py", line 193, in __call__
        self.call_service(*args, **kwargs)
      File "/projects/unicon/src/unicon/plugins/nso/service_implementation.py", line 262, in call_service
        self.result = con.command(cmd, reply=reply, error_pattern=error_pattern)
      File "/projects/unicon/src/unicon/bases/routers/services.py", line 197, in __call__
        return self.get_service_result()
      File "/projects/unicon/src/unicon/bases/routers/services.py", line 180, in get_service_result
        self.match_list)
    unicon.core.errors.SubCommandFailure: ('sub_command failure, patterns matched in the output:', ['----\\^'])
    >>>

If you want to avoid errors being detected with any command, you can pass an empty list to the settings object.

.. code-block:: python

    >>> from pyats.topology import loader
    >>>
    >>> tb = loader.load('testbed.yaml')
    >>> ncs = tb.devices.ncs
    >>>
    >>> ncs.connect(via='cli')
    >>> ncs.settings.ERROR_PATTERN=[]

The default error patterns can be seen by printing the settings.ERROR_PATTERN attribute.

.. code-block:: python

    >>> ncs.settings.ERROR_PATTERN
    ['Error:', 'syntax error', 'Aborted', 'result false']

Alternatively, you can pass an empty list when executing a command to avoid error pattern checking.

.. code-block:: python

    >>> c.execute('show command error', error_pattern=[])



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
style           str                       (optional) CLI style ('cisco' or 'juniper')
timeout         int (default 60 sec)      (optional) timeout value for the overall interaction.
reply           Dialog                    (optional) additional dialog object
error_pattern   list                      (optional) list of regex expressions to detect errors
=============   ======================    =====================================================

The `execute` service returns the output of the command in string format if a single command
is passed. If multiple commands are passed, the returned data is a dictionary with the commands
as keys and the responses as values. You can expect a TimeoutError, StateMachineError or 
SubCommandFailure error in case anything goes wrong.

This service can be used in 'exec' and 'config' modes of the CLI. The plugin will
automatically detect CLI state changes. You can use 'config', 'exit', 'end' and 'switch cli' 
commands to switch CLI state or CLI style, this will be detected automatically.

When you execute a command using the 'execute' service, the CLI style that is active before
execution will be restored at the end of the execution. This means that you cannot use
the `execute` service to switch styles, use the `cli_style` service for to change CLI style.
Executing the command `switch cli` by itself will raise an exception and point to cli_style.
You *can* use the 'switch cli' command as part of a series of commands to be executed.

The commands to execute can be specified as a single command, a newline separated list of 
commands, or a list of commands.

.. code-block:: python

    >>> response = ncs.execute('show services')
    >>> type(response)
    <class 'str'>
    >>> 

    >>> response = ncs.execute('show services\nshow devices list', style='cisco')
    >>> type(response)
    <class 'dict'>
    >>> 

    >>> response = ncs.execute(['show services','show devices list'], style='cisco')
    >>> type(response)
    <class 'dict'>
    >>>


configure
---------

The `configure` service is used to perform configuration on the CLI. It will change 
to configuration mode, execute the configuration command(s), commit the configuration
and change state back to exec mode.  If a failure is detected, the CLI state is changed
to exec mode, configuration changes are discarded and a `SubCommandFailure error` is raised.

=============   ======================    =====================================================
Argument        Type                      Description
=============   ======================    =====================================================
command         str, list                 configuration command(s) to execute
timeout         int (default 60 sec)      (optional) timeout value for the overall interaction.
reply           Dialog                    (optional) additional dialog object
error_pattern   list                      (optional) list of regex expressions to detect errors
=============   ======================    =====================================================

The configuration commands to execute can be specified as a single command, a newline separated 
list of commands or a list of commands. The `configure` service returns the output data in a
dictionary with the commands as keys and the responses as values. A dictionary is always returned
because the 'commit' command is always part of the execution. The `commit` command is added to
the commands automatically if it is not provided as part of the configuration command.

.. code-block:: python

    ncs.configure('services l3vpn foo endpoint PE1 pe-interface 0/0/0/1 ce CE1 ce-interface 0/1 ce-address 1.1.1.1 pe-address 1.1.1.2')

    config = """
    services l3vpn foo endpoint PE1 
    pe-interface 0/0/0/1 
    ce CE1 ce-interface 0/1 
    ce-address 1.1.1.1 
    pe-address 1.1.1.2
    """
    ncs.configure(config)


cli_style
---------

This service is used to switch the CLI style between Cisco and Juniper styles. This service will
execute 'switch cli' if the style needs to be changed. This is only supported by the ConfD main
plugin and is intended for NSO.

==========   ======================    ========================================
Argument     Type                      Description
==========   ======================    ========================================
style        str                       CLI style 'cisco' or 'juniper'
==========   ======================    ========================================

The style argument is a string, at minimum 'c' or 'j' should be passed, using
'cisco' and 'juniper' is also supported. You can switch CLI style in both exec and config modes.


command
-------

The `command` service is used by the execute and configure services to execute a single command 
on the CLI. You can use this service but the `execute` service is the preferred method.

=============   ======================    =====================================================
Argument        Type                      Description
=============   ======================    =====================================================
command         str                       command to execute
timeout         int (default 60 sec)      (optional) timeout value for the overall interaction.
reply           Dialog                    (optional) additional dialog object
error_pattern   list                      (optional) list of regex expressions to detect errors
=============   ======================    =====================================================

State changes in CLI will be detected, but to execute a command in a specific CLI style, 
you should use the `execute` service with the `style` option.

.. code-block:: python

    ncs.command("show services")


reload
------

Reload service for the ConfD plugin. Only supported with the CSP series. When used on the console
(i.e. via CIMC console), will return the reboot log. Console sessions will be detected automatically
based on the logs observed during the initial connection.

==============   ======================    =====================================================
Argument         Type                      Description
==============   ======================    =====================================================
reload_command   str                       command to execute to reload the device
timeout          int (default 600 sec)     (optional) timeout value for the overall interaction.
reply            Dialog                    (optional) additional dialog object
==============   ======================    =====================================================

.. code-block:: python

    # When running on the console, the boot log will be returned.
    boot_log = csp.reload()


.. sectionauthor:: Dave Wapstra <dwapstra@cisco.com>

