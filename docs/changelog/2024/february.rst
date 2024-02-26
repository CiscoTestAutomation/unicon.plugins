February 2024
==========

February 27 - Unicon v24.2 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.2 
        ``unicon``, v24.2 

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

* connection_provider
    * Updated try/except to log error message as warning

* unicon.eal
    * Add EOF handler for connection errors with telnet backend

* sshutils
    * Add a new pattern for add tunnel


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* utils
    * AbstractTokenDiscovey
        * Update the logic so the paltform set to sdwan if device is in controller mode.


