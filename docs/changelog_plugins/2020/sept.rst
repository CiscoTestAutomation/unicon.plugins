September 2020
--------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v20.9


Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon.plugins


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon.plugins


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

* [IOSXE] Added Traceroute service for Ha connection
* [IOSXE] Enhanced stack reload and switchover service
* [IOSXE] Enhanced disable_prompt and enable_prompt regex pattern

* [Junos] Updated regex to check more commit failures
* [Junos] Fix junos configure service duplicated commit

* [FXOS/FTD] Add 'Are you sure' statement - sendline(y)
* [FXOS] Add 'Invalid Command' and 'Ambiguous command' error patterns

* [Aireos] Add 'Warning' error_pattern
* [Aireos] Add error pattern checking during reload service

* [ASA] Add execute statement dialogs to execute service
* [ASA] Added reload_statements to reload service

* [NXOS] Update HA_INIT_CONFIG_COMMANDS to add 'line vty' and 'exec-timeout 0'
