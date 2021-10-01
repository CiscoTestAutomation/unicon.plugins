September 2021
========

September 28th
------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.9
        ``unicon``, v21.9

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

--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* iosxr
    * Fixed learn_hostname not working for iosxrv9k platform

* generic
    * Fix the default dialog statements used in reload services
    * Fix reload service to return True or False instead of raise an exception

* nxos
    * configure will raise incomplete command error when appropriate

* iosxr/spitfire
    * Use generic pre-connection statement list to handle syslog messages on connect

* linux
    * Add `sudo` service
