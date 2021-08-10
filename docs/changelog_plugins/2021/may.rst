May 2021
========

May 25th
--------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.5
        ``unicon``, v21.5

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

* iosxr/spitfire
    * Updated module prompt pattern

* documentation
    * Fix prompt pattern examples
    * Update docs for SSH passphrase credential

* unittests
    * Update unittests to reflect changes in connect() return

* sros
    * Automatically connect when calling execute() and device is not connected.
    * Add init commands

* nxos unittest
    * Added unittest to verify show logging output

* generic
    * Support enable secret prompts

* generic configure
    * Fix config state change where incorrect 'service prompt config' would be sent

* iosxe/csr1000v
    * Cleanup statemachine

* nxos
    * Add VDC detection logic

* iosxr
    * Update config error pattern

* eos
    * new plugin 'eos' for arista eos platform

* gaia
    * New plugin 'gaia' for Check Point Gaia OS platform


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * Added execute statement for 'Do you want to remove the above files?'

* nxos
    * Added configure error pattern to catch '% Ambiguous command at '^' marker.'
