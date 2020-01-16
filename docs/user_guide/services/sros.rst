SROS
====
This section lists all services for Nokia SR-OS.

mdcli_execute
-------------
Service to execute commands on device via MD-CLI.
Please refer to:
:doc:`Common Services  <generic_services>`

mdcli_configure
---------------
Service to configure commands on device via MD-CLI.
Please refer to:
:doc:`Common Services  <generic_services>`

One more different argument from `configure` of "Common Services":

=========  =====    ===========================================================
Argument   Type     Description
=========  =====    ===========================================================
mode       str      Configuration mode (exclusive, global, private, read-only)
=========  =====    ===========================================================

.. code-block:: python

        #Example
        --------
        cmd = 'router interface coreloop ipv4 primary address 1.1.1.1 prefix-length 32'
        output = device.mdcli_configure(cmd)
        output = device.mdcli_configure(cmd, mode='global')
        device.mdcli_configure.mode = 'global'
        output = device.mdcli_configure(cmd)

classiccli_execute
------------------
Service to execute commands on device via Classic CLI.
Please refer to:
:doc:`Common Services  <generic_services>`

classiccli_configure
--------------------
Service to configure commands on device via Classic CLI.
Please refer to:
:doc:`Common Services  <generic_services>`

switch_cli_engine
-----------------
Service to switch CLI engine.

=========  =====    ===========================================================
Argument   Type     Description
=========  =====    ===========================================================
engine     str      CLI engine name (mdcli, classiccli)
=========  =====    ===========================================================

get_cli_engine
--------------
Service to get current CLI engine name.

execute
-------
Service to execute commands on device via current CLI engine, eg. via mdcli_execute, classiccli_execute.

configure
---------
Service to configure commands on device via current CLI engine, eg. via mdcli_configure, classiccli_configure.

send
----
Service to send the **'command/string'** to spawned channel.
Please refer to:
:doc:`Common Services  <generic_services>`

sendline
--------
Service to send the **'command/string'** with "\r" to spawned channel.
Please refer to:
:doc:`Common Services  <generic_services>`

expect
------
Service to match a list of patterns against the buffer.
Please refer to:
:doc:`Common Services  <generic_services>`

expect_log
----------
Service to enable/disable expect debug log.
Please refer to:
:doc:`Common Services  <generic_services>`

log_user
--------
Service to enable/disable device log on screen.
Please refer to:
:doc:`Common Services  <generic_services>`

log_file
--------
Service to get or change device `FileHandler` file.
Please refer to:
:doc:`Common Services  <generic_services>`
