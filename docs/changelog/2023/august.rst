August 2023
==========

August 29 - Unicon v23.8
------------------------



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

* unicon.bases.linux
    * Added init_connection to connection provider
        * added init_connection method for initializing the device

* unicon
    * Added support for `os_flavor` as plugin selector attribute


--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* iosxe
    * stack
        * Update  mock data for stack devices for standby lock.


--------------------------------------------------------------------------------
                                      New
--------------------------------------------------------------------------------

* generic
    * Added recovery for Reload and HaRelaod
        * Recover device using golden image if reload is failed with an exception


