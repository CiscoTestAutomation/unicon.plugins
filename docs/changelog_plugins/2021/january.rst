January 2021
============

January 27th
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.1
        ``unicon``, v21.1

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

* GENERIC PLUGIN
    * 'Attach' Service Implementation.  This Requires Plugins To Support The 'Module' State.
    * Added 'Target_Standby_State' Keyword Argument For Rp_State Check In Reload Service
    * Updated Traceroute Service To Check For Valid Keyword Arguments
    * Added Configure Statement List Dialog To Configure Service

* NXOS PLUGIN
    * Added 'Attach' Service
    * Added Configure_Dual Service For Nxos Plugin
    * Fixed Configure Pattern To Enable Learning Hostname If The Device Is In Config State

* LINUX PLUGIN
    * Added Handler For 'Sudo' Password

* IOS, IOSXE, IOSXR PLUGINS
    * Added Configure Error Pattern To Ios, Iosxe And Iosxr

* DOCUMENTATION
    * Updated Dialog Docgen Script To Include Configure Dialogs

* IOSXE PLUGIN
    * Updated Configure Statement List To Handle Yes/No Prompt
    * Added Support For Grub Menu In The Reload Service

* APIC PLUGIN
    * Refactored Reload Service To Support Ssh Based Reloads
    * Added 'Shell' State

* ASA PLUGIN
    * Added Firepower 2K (Fp2K) Platform Support

* FXOS PLUGIN

* GENERIC
    * Add Support For Hostname Change With Non-Bulk Config Commands

* REMOVED ACI/APIC PLUGIN (USE OS APIC INSTEAD)

* REMOVED ACI/N9K PLUGIN (USE OS NXOS, PLATFORM=ACI INSTEAD)

* REMOVED NXOS/ACI/N9K PLUGIN (USE OS NXOS, PLATFORM=ACI INSTEAD)

* ALL PLUGINS
    * `Series` Has Been Renamed To `Platform`

* ADDED NEW HP COMWARE PLUGINS


