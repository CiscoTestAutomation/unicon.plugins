January 2024
==========

30 - Unicon v24.1 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.1 
        ``unicon``, v24.1 

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

* pty_backend
    * Modified error handling logic to allow dialog to process statements on subprocess exit

* utils
    * Update ansi pattern to allow imports

* statemachine
    * Update hostname logic to handle hostnames with special characters

* unicon
    * Add CLI option to enable debug logs


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* service_implementation
    * Modified Reload service
        * Removed sendline after reload

* iosxr
    * Modified moonshine UTs
        * Updated wrong import statements in standalone_ping_test.py and config_test.py UTs.


