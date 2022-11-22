July 2021
========

July 27
------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.7
        ``unicon``, v21.7

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

* connection provider
    * Added fix to clear the previous connection data for HA unlock_standby
    * Refactored HA initialization for dual RP connections

* mock device
    * changed basicConfig from stderr to stdout from mock device to prevent stderr output

* statemachine
    * Log warning when `add_state_pattern` is used

* prompt recovery
    * Use warning on hostname mismatch instead of raising exception

* mock device
    * Handle unicode errors and log error message if they occur

* playback
    * Enhanced not to show unexpected warning based on recording




