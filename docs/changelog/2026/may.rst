May 2026
==========

May 26 - Unicon v26.5
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.5 
        ``unicon``, v26.5 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe/cat9k
    * Updated `HARommon`
        * Ensures HA rommon breaks boot on all consoles via active reload plus parallel standby interrupts with improved state validation.

* iosxe/stack
    * Updated `StackStateMachine`
        * Refactored rommon path to include entire shelf reload and breakboot on all members.
        * update `StackRommon` to inherit from `IosXESingleRpStateMachine` to leverage existing rommon logic and ensure consistency with single RP devices.


