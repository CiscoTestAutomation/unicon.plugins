September 2022
==========

September 27 - Unicon v22.9
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.9
        ``unicon``, v22.9

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
                                      New
--------------------------------------------------------------------------------

* connection base
    * add option log_propagate to control whether logger for the connection propagates logs to parent
    * add option no_pyats_tasklog to prevent Unicon from adding pyats tasklog handler


--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* mock_device
    * Fixed issue with HA mode mock device when asyncssh package is not installed


