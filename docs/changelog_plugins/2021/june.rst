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

* generic
    * Updated switchover service, removed configure retry logic

* iosxe
    * Updated switchover service, renamed dialog argument to reply

* nxos
    * Remove VDC switchback from disconnect. No longer needed thanks to VDC detection.
    * Handle more prompt for 'show vdc' on connect

* generic
    * Mock device updates for device SSH command

* generic plugin
    * Refactor reload service
        * return complete console output if return_output=True
        * executes init commands after reload
        * reconnect if disconnected
        * wait at least POST_RELOAD_WAIT seconds for terminal to settle


