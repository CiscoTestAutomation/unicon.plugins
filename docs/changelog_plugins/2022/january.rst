January 2022
==========

January 25 - Unicon.Plugins v22.1 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.1 
        ``unicon``, v22.1 

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

* generic
    * Added `CONFIG_TRANSITION_WAIT` setting to allow changes the config transition wait time

* iosxe/iec3400
    * New plugin for IEC3400 device


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * Added new model under c9800 called c9800-cl
    * Added cat4k plugin

* hvrp
    * New plugin to connect to Huawei devices


