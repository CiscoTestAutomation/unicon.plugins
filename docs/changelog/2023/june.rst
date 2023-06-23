June 2023
==========

June 27 - Unicon v23.6 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v23.6 
        ``unicon``, v23.6 

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
    * Refactored backend to use telnetlib by default. All telnet connections will now use `telnetlib` implementation instead of system telnet.
    * Set `<connection_object>.settings.BACKEND = "unicon.eal.backend.pty_backend"` to revert to the system telnet client.

* unicon.mock
    * Update mock_device_cli to work with telnetlib backend


