January 2023
==========

January 31 - Unicon v23.1 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v23.1 
        ``unicon``, v23.1 

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
                            New
--------------------------------------------------------------------------------
* iosxe
    * Added Configure Error Patterns
        * "% SR feature is not configured yet, please enable Segment-routing first."
        * "% {address} overlaps with {interfaces}"
        * "%{interface} is linked to a VRF. Enable {protocol} on that VRF first."
        * "% VRF {vrf} not configured"
        * "% Incomplete command."
        * "%CLNS: System ID ({system_id}) must not change when defining additional area addresses"
        * "% Specify remote-as or peer-group commands first"
        * "% Policy commands not allowed without an address family"
        * Added switchover proceed pattern

--------------------------------------------------------------------------------
                                Fix
--------------------------------------------------------------------------------
* IOSXE
    * Add support for chassis keyword argument for bash console service
    
