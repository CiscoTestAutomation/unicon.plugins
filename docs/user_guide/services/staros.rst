StarOS
======

This section lists the services which are supported on Starent OS (staros).

  * `execute <#execute>`__
  * `configure <#configure>`__
  * `monitor <#monitor>`__

The following generic services are also available:

  * `send <generic_services.html#send>`__
  * `sendline <generic_services.html#sendline>`__
  * `expect <generic_services.html#expect>`__
  * `log_user <generic_services.html#log-user>`__


execute
-------

This service is used to execute arbitrary commands on the device. Though it is
intended to execute non-interactive commands. In case you wanted to execute
interactive command use `reply` option.


===============   ======================    ========================================
Argument          Type                      Description
===============   ======================    ========================================
timeout           int (default 60 sec)      timeout value for the overall interaction.
reply             Dialog                    additional dialog
command           str                       command to execute
===============   ======================    ========================================

`Execute` service returns the output of the command in the string format
or it raises an exception. You can expect a SubCommandFailure
error in case anything goes wrong.



.. code-block:: python

        #Example
        --------

        from unicon import Connection
        c=Connection(hostname='server',
                        start=['ssh server'],
                        os='cimc')

        output = c.execute("show chassis")


configure
---------

Service to configure device with list of `commands`. Config without
config_command will take device to config mode. Commands can be a string or
list. reply option can be passed for the interactive config command.
Use `prompt_recovery` argument for using `prompt_recovery` feature.

===============   ======================    ========================================
Argument          Type                      Description
===============   ======================    ========================================
timeout           int (default 30 sec)      timeout value for the command execution takes.
reply             Dialog                    additional dialog
command           str or list               string or list of commands to configure
prompt_recovery   bool (default False)      Enable/Disable prompt recovery feature
===============   ======================    ========================================


.. code-block:: python

        #Example
        --------

        output = rtr.configure()
        output = rtr.configure("no logging console")
        cmd =["no logging console"]
        output = rtr.configure(cmd)



monitor
-------

The monitor service can be used with the `monitor subscriber` command. You can pass
keyword arguments to configure settings for the monitor command.

===============   ======================    ========================================
Argument          Type                      Description
===============   ======================    ========================================
command           str                       monitor command to execute ('monitor' is optional)
                                            or 'stop' to stop the monitor.
<option_name>     str                       Name of the option to set
<option_name>     str                       Name of the option to set
...
===============   ======================    ========================================

Example:

.. code-block:: python

    mme.monitor('subscriber imsi 000110000000001', app_specific_diameter={'diameter_gy': 'on', 'diameter_gx_ty_gxx': 'on'})

    mme.monitor('subscriber next-call', stun='on', sessmgr='on')

All settings that follow the CLI output syntax of ``NN - Service name ( OFF)`` are
supported as long as the response for the status is similar to `*** Service name ( state) ***`.

The `Service Name` will be translated to `service_name` for use with keyword arguments.
E.g. ``13 - RADIUS Auth (ON )`` can be updated using keyword argument `radius_auth='off'`.

The option `app_specific_diameter` is a special case as it requires sub options to be
specified. You can pass sub options via a dictionary like this:

.. code-block:: python

    mme.monitor('subscriber imsi 000110000000001', app_specific_diameter={'diameter_gy': 'on'})

Similar to standard options, the names are translated from e.g. `DIAMETER Gx/Ty/Gxx` to
`diameter_gx_ty_gxx`.

Other non-standard options are `RADIUS Dictionary` and `GTPP Dictionary`, you can pass the
target value and the implementation will try to reach that by repeatedly sending the option
key(s) up to a maximum of known number of options. E.g. you can specify ``custom12`` as a
target for `radius_dictionary`.

.. code-block:: python

    mme.monitor('subscriber imsi 000110000000001', radius_dictionary='custom12')

The monitor service will start the command and return, you can use the sub-service ``monitor.tail``
to monitor the output on the console.

To stop the monitor and return the buffered output, use `output = mme.monitor('stop')`

You can inspect the current state of the monitor settings via the ``monitor.monitor_state`` object.
This is a dictionary with all the settings and their current values.

.. code-block:: python

      from pprint import pprint
      pprint(mme.monitor.monitor_state)



monitor.get_buffer
~~~~~~~~~~~~~~~~~~

To get the output that has been buffered by the monitor service, you can use the `monitor.get_buffer`
method. This will return all output from the start of the monitor command until the moment of execution
of this service.

=====================   ======================    ===================================================
Argument                Type                      Description
=====================   ======================    ===================================================
truncate                bool (default: False)     If true, will truncate the current buffer.
=====================   ======================    ===================================================

.. code-block:: python

    output = mme.monitor.get_buffer()


monitor.tail
~~~~~~~~~~~~

The monitor.tail method can be used to monitor the output logging after the ``monitor`` service
has been used to start the monitor. If you pass the option `return_on_match=True`, the
output will be returned when the call finished pattern (default: ``Call Finished``) is seen.

=====================   ======================    ===================================================
Argument                Type                      Description
=====================   ======================    ===================================================
timeout                 int (seconds)             maximum time to wait before returning output.
pattern                 str (regex)               Regex pattern to monitor for (default: .*Call Finished.*)
return_on_match         bool (default: True)      If True, returns output if pattern is seen.
stop_monitor_on_match   bool (default: False)     Stops the monitor session if True.
=====================   ======================    ===================================================


.. code-block:: python

    output = mme.monitor.tail(timeout=300, return_on_match=True, stop_monitor_on_match=True)


monitor.stop
~~~~~~~~~~~~

Stop the monitor.
