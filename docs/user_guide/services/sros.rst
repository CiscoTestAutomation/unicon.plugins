SROS
====
This section lists all services for Nokia SR-OS.

mdcli_execute
-------------
Service to execute commands on device via MD-CLI.
For more arguments and examples, please refer to generic "execute" service:
:doc:`Common Services  <generic_services>`

.. code-block:: python

        #Example
        --------
        output = device.mdcli_execute('show version')
        output = device.mdcli_execute('show router interface "coreloop"')

mdcli_configure
---------------
Service to configure commands on device via MD-CLI.
For more arguments and examples, please refer to generic "configure" service:
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
        output = device.mdcli_configure(cmd)  # configure on default mode "private"
        output = device.mdcli_configure(cmd, mode='global')  # configure on mode "global"
        device.mdcli_configure.mode = 'global'  # change default mode to "global"
        output = device.mdcli_configure(cmd)  # configure on mode "global"

classiccli_execute
------------------
Service to execute commands on device via Classic CLI.
For more arguments and examples, please refer to generic "execute" service:
:doc:`Common Services  <generic_services>`

.. code-block:: python

        #Example
        --------
        output = device.classiccli_execute('show version')
        output = device.classiccli_execute('show router interface "coreloop"')

classiccli_configure
--------------------
Service to configure commands on device via Classic CLI.
For more arguments and examples, please refer to generic "configure" service.
Please refer to:
:doc:`Common Services  <generic_services>`

.. code-block:: python

        #Example
        --------
        cmd = 'configure router interface "coreloop" address 111.1.1.1 255.255.255.255'
        output = device.classiccli_configure(cmd)

switch_cli_engine
-----------------
Service to switch CLI engine.

=========  =====    ===========================================================
Argument   Type     Description
=========  =====    ===========================================================
engine     str      CLI engine name (mdcli, classiccli)
=========  =====    ===========================================================

.. code-block:: python

        #Example
        --------
        device.switch_cli_engine('mdcli')
        device.switch_cli_engine('classiccli')

get_cli_engine
--------------
Service to get current CLI engine.

.. code-block:: python

        #Example
        --------
        current_engine = device.get_cli_engine()

execute
-------
Service to execute commands on device via current CLI engine, eg. via service mdcli_execute or classiccli_execute.

.. code-block:: python

        #Example
        --------
        device.switch_cli_engine('mdcli')
        output = device.execute('show version')  # execute by mdcli_execute

        device.switch_cli_engine('classiccli')
        output = device.execute('show router interface "coreloop"')  # execute by classiccli_execute

configure
---------
Service to configure commands on device via current CLI engine, eg. via service mdcli_configure or classiccli_configure.

.. code-block:: python

        #Example
        --------
        device.switch_cli_engine('mdcli')
        output = device.configure('router interface coreloop ipv4 primary address 1.1.1.1 prefix-length 32')  # configure by mdcli_configure
        output = device.configure('delete router interface "coreloop" ipv4', mode='private')  # configure by mdcli_configure

        device.switch_cli_engine('classiccli')
        output = device.configure('configure router interface "coreloop" address 111.1.1.1 255.255.255.255')  # configure by classiccli_configure

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
