StarOS
======

This section lists the services which are supported on Starent OS (staros).

  * `execute <#execute>`__
  * `configure <#configure>`__

The following generic services are also avaiable:

  * `send <generic_services.html#send>`__
  * `sendline <generic_services.html#sendline>`__
  * `expect <generic_services.html#expect>`__
  * `expect_log <generic_services.html#expect-log>`__
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
Refer :ref:`prompt_recovery_label`  for details
on prompt_recovery feature.

===============   ======================    ========================================
Argument          Type                      Description
===============   ======================    ========================================
timeout           int (default 60 sec)      timeout value for the command execution takes.
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


