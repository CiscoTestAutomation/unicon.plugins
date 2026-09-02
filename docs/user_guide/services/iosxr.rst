IOSXR
=====

This section lists down all those services which are only specific to IOSXR.
For list of all the other service please refer this:
:doc:`Common Services  <generic_services>`.

.. important::

    In argument table

    * values in parenthesis are default values.
    * mandatory arguments are marked with `*`.


attach_console
--------------

Service to attach to line card console to execute commands in. Returns a
router-like object to execute commands on using python context managers.

====================    ======================    ========================================
Argument                Type                      Description
====================    ======================    ========================================
module_num              str                       slot number to attach console to
login_name              str                       name to login with,
default_escape_chars    str                       default escape char, default: exit,
change_prompt           str                       new prompt to change to for ez automation
timeout                 int (default 60 sec)      timeout in sec for executing commands
prompt                  str                       bash prompt (default # )
====================    ======================    ========================================

.. code-block:: python

    with device.attach_console('0/RP0/CPU0') as conn:
        output1 = conn.execute('ls')
        output2 = conn.execute('pwd')


admin_attach_console
--------------------

Service to attach to line card console from admin bash to execute commands in. Returns a router-like object to execute commands on using python context
managers.

====================    ======================    ========================================
Argument                Type                      Description
====================    ======================    ========================================
module_num              str                       slot number to attach console to
login_name              str                       name to login with,
default_escape_chars    str                       default escape char, default: exit,
change_prompt           str                       new prompt to change to for ez automation
timeout                 int (default 60 sec)      timeout in sec for executing commands
prompt                  str                       bash prompt (default ``[sysadmin-vm:0_\w+:~]$`` )
====================    ======================    ========================================

.. code-block:: python

    with device.admin_attach_console('0/RP0') as conn:
        output1 = conn.execute('ls')
        output2 = conn.execute('pwd')


admin_bash_console
------------------

Service to execute commands in the router Bash from admin prompt. ``admin_bash_console``
gives you a router-like object to execute commands on using python context
managers.

==========   ======================    ========================================
Argument     Type                      Description
==========   ======================    ========================================
timeout      int (default 60 sec)      timeout in sec for executing commands
prompt       str                       bash prompt (default ``[sysadmin-vm:0_\w+:~]$`` )
==========   ======================    ========================================

.. code-block:: python

    with device.admin_bash_console() as bash:
        output1 = bash.execute('ls')
        output2 = bash.execute('pwd')


admin_console
-------------

Service to execute commands in admin prompt. ``admin_console``
gives you a router-like object to execute commands on using python context
managers.

==========   ======================    ========================================
Argument     Type                      Description
==========   ======================    ========================================
timeout      int (default 60 sec)      timeout in sec for executing commands
prompt       str                       bash prompt (default: ``sysadmin-vm:0_\w+#`` )
==========   ======================    ========================================

.. code-block:: python

    with device.admin_console() as bash:
        output1 = bash.execute('show platform')
        output2 = bash.execute('show version')


admin_execute
-------------

Service to execute commands under admin state.
Has same arguments as generic execute service.

.. code-block:: python

    output = device.admin_execute('show version')


admin_configure
---------------

Service to configure device under admin-config state.
Has same arguments as generic configure service.

.. code-block:: python

    output = device.admin_configure('no logging console')


configure_exclusive
-------------------

Service to configure device while locking the
router configuration. The system configuration can be made
only from the login terminal.
Has same arguments as generic configure service.

.. code-block:: python

    output = device.configure_exclusive('logging console disable')


monitor
-------

The monitor service can be used with the `monitor interface` command. You can
also pass `action` commands to execute while the monitor is running. For
example `clear` (lowercase) will send the key associated with the action as
shown in the output, i.e. Clear="c" will send "c" for action "clear".

===============   ======================    ==================================================
Argument          Type                      Description
===============   ======================    ==================================================
command           str                       monitor command to execute ('monitor' is optional)
                                            or action to send (e.g. 'clear')
reply             Dialog                    additional dialog
timeout           int (default 60 sec)      timeout value for the overall interaction.
===============   ======================    ==================================================

Example:

.. code-block:: python

    rtr.monitor('monitor interface GigabitEthernet0/0/0/0')

    # execute `monitor interface`
    rtr.monitor('interface')

    # tail the output for 10 seconds
    rtr.monitor.tail(timeout=10)

    output = rtr.monitor.stop()

    # send an action to the device
    rtr.monitor('clear')
    rtr.monitor('bytes')
    rtr.monitor('general')
    rtr.monitor('IPv4 uni')  # this can be called with 'ipv4 uni' or 'ipv4uni' as well.


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

    output = rtr.monitor.get_buffer()


monitor.tail
~~~~~~~~~~~~

The monitor.tail method can be used to monitor the output logging after the ``monitor`` service
has been used to start the monitor.

=====================   ======================    ===================================================
Argument                Type                      Description
=====================   ======================    ===================================================
timeout                 int (seconds)             maximum time to wait before returning output.
=====================   ======================    ===================================================

.. code-block:: python

    output = rtr.monitor.tail(timeout=30)


monitor.stop
~~~~~~~~~~~~

Stop the monitor and return all output.

.. code-block:: python

    output = rtr.monitor.stop()


Sub-Plugins
-----------

Spitfire
^^^^^^^^

The spitfire sub plugin supports all services provided by :doc `Common Services <generic_services>`.

In addition to the common services spitfire also supports the following services

attach_console
""""""""""""""

Service to attach to line card console/Standby RP to execute commands in. Returns a
router-like object to execute commands on using python context managers.This service is
supported in HA as well.

====================    ======================    ========================================
Argument                Type                      Description
====================    ======================    ========================================
module_num              str                       slot number to attach console to
login_name              str                       name to login with,
default_escape_chars    str                       default escape char, default: exit,
change_prompt           str                       new prompt to change to for ez automation
timeout                 int (default 60 sec)      timeout in sec for executing commands
prompt                  str                       bash prompt (default # )
====================    ======================    ========================================

.. code-block:: python

    with device.attach_console('0/0/CPU0') as conn:
        output1 = conn.execute('ls')
        output2 = conn.execute('pwd')

switchto
""""""""

Service to switch the router console to any state that user needs in order to perform
his tests. The api becomes a no-op if the console is already at the state user wants
to reach. This service is supported in HA as well.


The states available to switch to are :

* enable
* config
* bmc
* xr_bash
* xr_run
* xr_env

====================    ======================    ========================================
Argument                Type                      Description
====================    ======================    ========================================
target_state            str                       target state user wants the console at
timeout                 int (default in None)     timeout in sec for executing commands
====================    ======================    ========================================

.. code-block:: python

        device.switchto("xr_env")
        .... some commands that need to be run in xr_env state ....
        device.switchto("enable")
