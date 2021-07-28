July 2021
========

July 27th
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

* iosxe
    * removed basicConfig from mock device to prevent stderr output
    * Updated statemachine standby locked state detection

* aireos
    * removed basicConfig from mock device to prevent stderr output

* asa
    * removed basicConfig from mock device to prevent stderr output

* confd
    * removed basicConfig from mock device to prevent stderr output

* dell/dellos6
    * removed basicConfig from mock device to prevent stderr output

* eos
    * removed basicConfig from mock device to prevent stderr output

* fxos
    * removed basicConfig from mock device to prevent stderr output

* gaia
    * removed basicConfig from mock device to prevent stderr output

* hpcomware
    * removed basicConfig from mock device to prevent stderr output

* ios
    * removed basicConfig from mock device to prevent stderr output

* iosxr
    * removed basicConfig from mock device to prevent stderr output

* ironware
    * removed basicConfig from mock device to prevent stderr output

* junos
    * removed basicConfig from mock device to prevent stderr output

* nxos
    * removed basicConfig from mock device to prevent stderr output

* vos
    * removed basicConfig from mock device to prevent stderr output

* generic
    * Removed disconnect/connect from HA reload
    * Fixed state transition on ping failure

* generic
    * Updated Reload in service_implementation.py

* general
    * Updated ``guestshell`` service for use with IOSXE and NXOS


--------------------------------------------------------------------------------
                                      New
--------------------------------------------------------------------------------

* nxos/mds
    * Add support for Target Initiator Emulator (TIE)




