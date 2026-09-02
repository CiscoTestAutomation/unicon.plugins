April 2026
==========

April 28 - Unicon v26.4
-----------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.4
        ``unicon``, v26.4




Changelogs
^^^^^^^^^^

--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* mock
    * Modified MockDevice
        * Handle PTY Ctrl-C interrupts in the core mock device run loop so


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe
    * Modified ``boot_image`` / settings
        * Added support for ordered ``BOOT_FILE_REGEX`` lists so discovered boot images are queued by regex priority across filesystems.

* iosxe/ie3k
    * Modified ``IosXEIe3kSettings``
        * Updated boot image selection to prioritize ``.SSA.bin``, then ``.SPA.bin``, then other ``.bin``images through ordered``BOOT_FILE_REGEX`` entries.

* iosxe/cat9k
    * Modified ``Rommon``&``HARommon`` service implementation
        * Updated enable break regex to handle 'no' option for ENABLE_BREAK variable.
    * Modified ``HARommon``
        * Ensures HA rommon breaks boot on all consoles via active reload plus parallel standby interrupts with improved state validation.


