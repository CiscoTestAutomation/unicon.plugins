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

* iosxe/cat8k
    * Updated switchover implementation
        * Added POST_SWITCHOVER_WAIT setting
        * Added missing context to dialog
        * Added option to return output

* iosxe
    * Added support for ROMMON init commands

--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * Added new model under c9800 called c9800-cl
    * Added cat4k plugin

* hvrp
    * New plugin to connect to Huawei devices

* iosxe/c9800/ewc_ap
    * Add new plugin for C9800/EWC_AP platform

* utils
    * Added AbstractTokenDiscovery
        * Added mechanism to learn, standardize, and apply device abstraction tokens

* nxos
    * Added l2rib client support to statemachine
    * New `l2rib_dt` service