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


EnXR
^^^^^^^^

EnXR is a device simulator based on an XR image and it is used for development.
It is a development platform for running platform independent IOS XR code on Linux. It consists of an implementation of
the IOS XR platform layer to enable PI code to run on Linux servers, and also tools to support the building and testing
of code on those servers.

Connectivity with the EnXR
""""""""""""""""""""""""""

To connect the pyATS with the EnXR device, you first need to pull enxr workspace in your
ADS. EnXR pulling is clearly mentioned in the :ref:'Setting EnXR Device'

Then you need to install pyATS & it is recommended to install the pyATS inside your EnXR
workspace.


Installing pyATS
""""""""""""""""

/auto/pyats/bin/pyats install --py-home <python3 interpreter path in your ADS> --no-git

* To know the path of your python3 interpreter, you can run which python3 on your ADS.
And the path you get, needs to put as an argument for --py-home option.


Setting up EnXR Device
"""""""""""""""""""

To setup the EnXR device, You can follow the below steps:

1. ssh <your ADS> (must be CEL7 or above)
2. cd /nobackup/<CEC username>/
3. mkdir enxr
4. cd enxr
5. acme pull -sb ios_ena -lineup xr-dev.lu -plat enxr
6. tools/misc/xr_bld -core -plat enxr
7. lboot -m (wait for config to load)
8. exec
9. conf t
10. netconf-yang agent ssh
11. commit
12. end
13. Leave terminal open and start new terminal
14. ssh <your ADS>
15. cd /nobackup/<CEC username>/enxr
16. lboot -mc
17. netconf_sshd_proxy -i 0 -o 1 -u lab
18. IF YOU DO NOT SEE A NETCONF HELLO PACKET RESPONSE, EnXR IS NOT WORKING!!!

Connecting with the EnXR
""""""""""""""""""""""""
Below is the example code to connect with the enxr device and execute command
.. code-block:: python

        from pyats.topology import loader
        topo=loader.load('testbed_memory_native_enxr.yml')
        dev=topo.devices['bgl-ads-4861']
        dev.connect(via='cli', alias='ssh')
        showrun=dev.ssh.execute('show run')
