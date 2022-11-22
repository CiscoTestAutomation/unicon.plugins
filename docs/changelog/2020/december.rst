December 2020
=============

December 15th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v20.12
        ``unicon``, v20.12


Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon.plugins
    bash$ pip install unicon


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon.plugins
    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

* IOSXE plugin
    - Updated regex for config prompt
    - Fixed patterns and added ca_profile for its config to be matched
* IOSXR plugin
    * NCS5K plugin
        - Fixed HA Reload to use correct credentials
* NXOS ACI Plugin
    * Added configure service
    * Removed deprecation message from nxos->aci->n9k
    * Fixed a bug where the buffer might not be empty after connecting to the device
* ASA Plugin
    - Add error_pattern to capture `*** WARNING ***`
* FXOS/FTD Plugin
    - Added support for "* " in chassis prompt, e.g. "FirePower* #"
* Linux
    * Added passphrase pattern in connection dialogs
    * Made it possible to override the shell prompt from the connection settings
* Core
    * Added feature to extend list settings from testbed file
    * Fixed log issue when pyats managed_handlers's tasklog stream is None
    * Fixed parse_spawn_command for ha device to get the right subconnection context
    * Fixed ssh command username issue
    * Enhacnced ha device connectivity check
