March 2021
==========

March 30th
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.3
        ``unicon``, v21.3

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

* statemachine
    * detect_state() now passes the connection context to go_to()

* connections
    * Refactor is_connected to use connected implementation
    * Fix bug with file descriptor on disconnect/close

* device ERROR_PATTERN settings
    * Add integration test for device settings from topology

* device custom settings
    * Added support for execute, configure and traceroute timeouts from custom key for backward compatibility with Genie


