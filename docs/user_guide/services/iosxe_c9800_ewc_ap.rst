IOSXE/C9800/EWC_AP
==================

This section lists down all those services which are only specific to C9800/EWC_AP platform/model.

For list of all the other service please refer this:
:doc:`Common Services  <generic_services>`.


bash_console
------------

Service to execute commands in the router Bash. ``bash_console``
gives you a router-like object to execute commands on using python context
managers.

After entering bash shell, the commands in `BASH_INIT_COMMANDS` setting are executed.

==========   ======================    ========================================
Argument     Type                      Description
==========   ======================    ========================================
chassis      int (default: 1)          Chassis identifier to connect to
timeout      int (default 60 sec)      timeout in sec for executing commands
target       str                       'standby' to bring standby console to bash.
==========   ======================    ========================================

.. code-block:: python

    with device.bash_console() as bash:
        output1 = bash.execute('ls')
        output2 = bash.execute('pwd')


ap_shell
--------

Service to bring the device to AP shell and execute commands.

When entering the shell, the `HA_INIT_EXEC_COMMANDS` from the `cheetah/ap` plugin settings
will be executed.

===============   =======================     =============================================
Argument          Type                        Description
===============   =======================     =============================================
timeout           int                         timeout value in sec, Default Value is 60 sec
===============   =======================     =============================================

.. code-block:: python

        # bring device to rommon mode
        with device.ap_shell() as shell:
            shell.execute('show version')

