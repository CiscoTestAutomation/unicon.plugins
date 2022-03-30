February 2022
==========

February 24 - Unicon.Plugins v22.2 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.2 
        ``unicon``, v22.2 

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

* utils
    * Modified AbstractTokenDiscovery
        * Extended prompt dialog to handle output containing "--More--"
    * Modified load_pid_token_csv_file
        * Renamed to load_token_csv_file
        * Adjusted logic to support dynamic csv loading based on header fields
        * Added an optional `key` argument to allow for different keys to be specified other than pid


