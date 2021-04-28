April 2021
==========

April 27th
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.4
        ``unicon``, v21.4

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

* AIREOS PLUGIN
    * Add Error_Pattern For ^[Rr]Equest [Ff]Ailed And R'^(.*?) Already In Use'
    * Add Error_Pattern For R'Wlan Identifier Is Invalid' And R'^Request Failed'

* NXOS/ACI
    * Inherit Services From Nxos Plugin

* GENERIC PLUGIN
    * Add Syslog Message Handler To Connect, Execute And Configure Services

* IOSXE/CAT9K
    * Support `Rommon()` And `Reload()` Services

* GENERIC EXECUTE AND CONFIGURE SERVICES
    * Added `Append_Error_Pattern` Argument

* NXOS
    * Added `Skip_Poap` Statement For Reload Service

* NXOS PLUGIN
    * Add Dialog To Handle Commit Confirm Message
    * Use 'Commit' As Default Commit Command For Configure_Dual Service


--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* NXOS/ACI
    * Attach_Console Service For Nxos/Aci Plugin

* IOSXR
    * Updated `Run_Prompt` Pattern To Accept More Variety

* IOSXR/SPITFIRE
    * Fixed Failed Config Handling When Transitioning From Config To Enable State

* IOSXR/MOONSHINE
    * Updated Shell Prompt Pattern

* AIREOS PLUGIN
    * Changed Error_Pattern '^(%\S*)?Error' To '^(%\S*)?(Error|Error)' So It Is Case Insensitive

* JUNOS PLUGIN
    * Update Configure Service, Allow Commit_Cmd Override

* IOSXE
    * Updated Config Prompt Pattern To Include "Cloud"

* IOSXE/CSR1000V
    * Use Iosxe Config Prompt Pattern

* GENERAL
    * Use Plugin Specific Config Prompt For Config State Transition
    * Enable 'Service Prompt Config' If We Detect No Prompt On Config Transition

* SETUP.PY
    * Update Version Check To Allow Users To Build Local Versions


