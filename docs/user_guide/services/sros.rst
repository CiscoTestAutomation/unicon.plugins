SROS
====

This section documents the services available for Nokia SR-OS (a.k.a. TiMOS).
The implementations to Nokia SR-OS follows documentation available at:
https://infocenter.nokia.com/public/7750SR160R1A/index.jsp?topic=%2Fcom.sr.mdcli%2Fhtml%2Fusing_mdcli.html


switch_cli_engine
-----------------

API to switch CLI engine for this device connection

=========  =====    ===========================================================
Argument   Type     Description
=========  =====    ===========================================================
engine     str      CLI engine name (mdcli, classiccli)
=========  =====    ===========================================================

.. code-block:: python

        # Example
        # -------

        # switch to md-cli
        device.switch_cli_engine('mdcli')

        # switch to classic-cli
        device.switch_cli_engine('classiccli')

get_cli_engine
--------------

returns the current cli-engine set for this device connection.

.. code-block:: python

        # Example
        # -------

        current_engine = device.get_cli_engine()


execute
-------

Similar to generic "execute" service, this api runs arbitrary commands on the
target device, which yields output, and returns to prompt.

This API will issue the provided command on **current** active CLI engine, 
internally calling the respective "specific command". Eg:

- if the device is in **MD-CLI** mode, issues command using ``mdcli_execute``

- if the device is in **classic-CLI** mode, issues command using 
  ``classiccli_execute``

.. code-block:: python

        # Example
        # -------
        
        # set to md-cli mode
        device.switch_cli_engine('mdcli')

        # device.execute() will now issue command using mdcli mode
        output = device.execute('show version')

        # switch back to classic cli mode, and issue classic-cli commands
        device.switch_cli_engine('classiccli')
        output = device.execute('show router interface "coreloop"')

configure
---------

Similar to generic "configure" service, this api applies the provided config
to target device and commits it.

This API will issue the provided command on **current** active CLI engine, 
internally calling the respective "specific command". Eg:

- if the device is in **MD-CLI** mode, issues command using ``mdcli_configure``

- if the device is in **classic-CLI** mode, issues command using 
  ``classiccli_configure``

This API accepts a positional argument ``mode`` (used by md-cli), specifying 
the config mode. Defaults to ``mode='private'``.

.. code-block:: python

        # Example
        # -------

        # set to md-cli
        device.switch_cli_engine('mdcli')

        # apply configuration
        output = device.configure('router interface coreloop ipv4 primary address 1.1.1.1 prefix-length 32')

        # apply configuration using specific configuration mode
        # (default mode is 'private', and can be changed via configuration)
        output = device.configure('delete router interface "coreloop" ipv4', mode='private')

        # switch to classic-cli & apply config
        device.switch_cli_engine('classiccli')
        output = device.configure('configure router interface "coreloop" address 111.1.1.1 255.255.255.255')


mdcli_execute
-------------

The specific service that implements ``execute()`` api under MD-CLI

.. code-block:: python

        # Example
        # -------
        output = device.mdcli_execute('show version')
        output = device.mdcli_execute('show router interface "coreloop"')

mdcli_configure
---------------

The specific service that implements ``configure()`` api under MD-CLI


One more different argument from `configure` of "Common Services":

=========  =====    ===========================================================
Argument   Type     Description
=========  =====    ===========================================================
mode       str      Configuration mode (exclusive, global, private, read-only)
=========  =====    ===========================================================

.. code-block:: python

        # Example
        # -------

        cmd = 'router interface coreloop ipv4 primary address 1.1.1.1 prefix-length 32'
        output = device.mdcli_configure(cmd)  # configure on default mode "private"
        output = device.mdcli_configure(cmd, mode='global')  # configure on mode "global"
        device.mdcli_configure.mode = 'global'  # change default mode to "global"
        output = device.mdcli_configure(cmd)  # configure on mode "global"

classiccli_execute
------------------

The specific service that implements ``execute()`` api under Classic-CLI

.. code-block:: python

        # Example
        # -------

        output = device.classiccli_execute('show version')
        output = device.classiccli_execute('show router interface "coreloop"')

classiccli_configure
--------------------
The specific service that implements ``configure()`` api under classic-CLI

.. code-block:: python

        # Example
        # -------

        cmd = 'configure router interface "coreloop" address 111.1.1.1 255.255.255.255'
        output = device.classiccli_configure(cmd)



Other Services
--------------

The following low-level, generic services are also supported for Nokia SR-OS. 
See :doc:`Common Services  <generic_services>` documentation for usage details.

- ``send``
- ``sendline``
- ``expect``
- ``log_user``
- ``log_file``
