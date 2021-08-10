September 2019
==============

September 24th
--------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.9


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
- core

  - Enhance SSHTunnel for multi-threaded connect

  - Add changes to correct the invalid learned_hostname

  - Add testbed YAML patchability for connection arguments, settings and service attributes

  - Add changes to allow user-defined dialog on connect

  - Log exception details when connection fails

- generic plugin

  - Enhance execute service to remove backspaces and previous characters from command output

  - Use POST_HA_RELOAD_CONFIG_SYNC_WAIT for HAReloadService to bring standby into any state

- asa plugin

  - New asa/asav plugin

- linux plugin

  - Add Linux return code check feature

- iosxr plugin

  - Fix HAReloadService for iosxr
