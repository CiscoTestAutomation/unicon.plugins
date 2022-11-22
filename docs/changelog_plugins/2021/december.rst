December 2021
=============

December 14 - Unicon.Plugins v21.12
-----------------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.12
        ``unicon``, v21.12

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

* iosxe
    * Added tclsh support
    * Added cat8k plugin


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxr/spitfire
    * Update the default init exec commands to use full terminal command

* generic
    * Added permission denied statement using a unicon core pattern
    * Modified service implementation
        * Corrected service log message

* nxos
    * Fix reload to use reconnect_sleep argument as buffer settle wait time

* iosxe
    * Modified service implementation
        * Corrected service log message


