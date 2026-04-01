March 2026
==========

March 31 - Unicon.Plugins v26.3 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.3 
        ``unicon``, v26.3 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* generic
    * Configure service
        * Refactored banner handling logic to improve maintainability.
        * Updated banner processing to send lines sequentially with appropriate delays for device processing.
    * HAReloadService
        * Fixed command fallback check and added guard to skip sendline when command is empty.
    * SwitchoverService
        * Fixed command fallback check and added guard to skip sendline when command is empty.

* iosxe
    * Configure service
        * Updated ACM configlet implementation to use connection context for acm_configlet parameter.
        * Ensures proper persistence of acm_configlet during state transitions.
        * Fixed multiline banner configuration to support variable delimiters
    * HASwitchover
        * Changed default command parameter from [] to None.

* iosxe/cat9k
    * stackwise_virtual
        * Updated the logic to detect current state before during state change
        * Updated the logic of designate handles to correctly identify active and standby state after svl configuration.
    * 9500x/stackwise_virtual
        * Updated the logic to detect current state before during state change

* iosxe/cat4k
    * Reload
        * Fixed reload_command fallback check and added guard to skip sendline when empty.

* iosxe/cat8k
    * SwitchoverService
        * Fixed command fallback check and added guard to skip sendline when empty.

* iosxe/stack
    * StackSwitchover
        * Fixed command fallback check and added guard to skip sendline when empty.
    * StackReload
        * Fixed reload_command fallback check and added guard to skip sendline when empty.

* iosxe/quad
    * QuadSwitchover
        * Fixed command fallback check and added guard to skip sendline when empty.
    * QuadReload
        * Fixed reload_command fallback check and added guard to skip sendline when empty.

* iosxe/cat9k/c9350/stack
    * C9350StackReload
        * Fixed reload_command fallback check and added guard to skip sendline when empty.

* iosxe/cat9k/c9500x/stackwise_virtual
    * SVLStackReload
        * Fixed reload_command fallback check, added guard for empty command and improved post-reload recovery and reconnection handling.
    * SVLStackSwitchover
        * Fixed command fallback check and added guard to skip sendline when empty.


