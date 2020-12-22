April 2020
=============

April 28th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v20.4


Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon.plugins


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon.plugins


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

* Enhanced aci plugin implementation to have it available under nxos plugins

* Update prompt for latest OpenSSH.

* Enhance IOSXR enable pattern to accomodate different preceding card/slot.

* Adding `copy` service to the HA IOSXE plugin implementation.

* Supporting `reset_standby_rp` on IOSXE.

* Updating XR spitfire plugin run prompts pattern.

* Updating XR spitfire plugin run prompts pattern.

* Updating mdcli and classiccli prompts pattern.

* Fixed aci plugins unittests and added new ones for the new plugins structure.

* Updating XR spitfire plugin run prompts pattern.

* Add 'Incorrect input' and 'HELP' error pattern for Aireos plugin

* Add nxos plugin configure error pattern for 'ERROR' and 'Invalid number'

* Fixing unittest after recent user contribution on standby behavior

* AireOS plugin updates:
    * HA support for WLC
    * Access Point (ap) as subplugin

* Added SSH passphrase handler to generic plugin

* Added Windows plugin
