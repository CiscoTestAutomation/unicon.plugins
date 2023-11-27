August 2023
===========

August 29 - Unicon.Plugins v23.8
--------------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v23.8
        ``unicon``, v23.8

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




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      New
--------------------------------------------------------------------------------

* unicon
    * Added support for os_flavor as plugin selector attribute
* unicon.bases.linux
    * Added init_connection to connection provider:
        * added init_connection method for initializing the device


--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* iosxe
    * stack:
        * Update  mock data for stack devices for standby lock.
* cheetah
    * Add support for devshell in cheetah OS based wireless access points
* iosxe
    * Update enable secret setup dialog logic to support devices without password or with short password
* Generic
    * Added recovery for Reload and HaRelaod:
        * Recover device using golden image if reload is failed with an exception
