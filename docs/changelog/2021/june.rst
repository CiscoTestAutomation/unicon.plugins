June 2021
========

June 29
------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.6
        ``unicon``, v21.6

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

* iosxe/sdwan
    * Added configure dialog statement for commit 'Proceed' prompt

* topology
    * Fix handling of debug keyword argument

* connection
    * Modified logic in 'connected' check to improve remote disconnect detection
    * Added warning log message if reconnect occurs

* unicon.eal.dialogs
    * Fixed `sendline_cred_user` and `sendline_cred_pass` implementation

* generic
    * Do not insert username for device SSH command

