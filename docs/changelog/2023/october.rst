October 2023
============

October 31 - Unicon v23.10
--------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v23.10
        ``unicon``, v23.10

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
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon.eal.backend
    * Added telnetlib backend.
    * Set `<connection_object>.settings.BACKEND = "auto"` to use the new telnetlib backend.

* unicon.mock
    * Update mock_device_cli to work with telnetlib backend

* unicon.bases.connection
    * learn_hostname
        * skip hostname learning if the device is in bash shell.

* unicon.bases.routers
    * Modified BaseSingleRpConnectionProvider
        * Updated establish_connection method to update cred_list in context if login_creds is not None


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* unicon.adapters
    * updated topology
        * add fallback credentials to the context for each connection.
        * Update pattern for invalid password.


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* cheetah
    * ap
        * Added support for device reload.


