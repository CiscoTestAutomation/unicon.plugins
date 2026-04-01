March 2026
==========

March 31 - Unicon v26.3 
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

* bases/router/connection_provider
    * Added logic to raise a traceback when when HA sync does not complete within POST_BOOT_TIMEOUT

* removed unused `pyats` and `genie` imports


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe/ie9k
    * Added plugin settings for IE9k platform.

* iosxe/ie3k
    * Added plugin settings for IE3k platform.


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe
    * Fixed boot image to support multiple filesystems.
    * Fixed encryption selection criteria on boot.

* iosxe/iec3400
    * Removed this platform as it must be ie3k.
    * Related state machine and test cases were not needed hence weren't moved to ie3k.

* pid_tokens.csv
    * Modified PID tokens
        * Added IE9k family PID token mappings.
        * Added ESS3300/ESS9300 family PID token mappings.

* pid_tokens
    * Added PID tokens for IE 3100, 3500 series

* iosxe/settings
    * Increased POST_BOOT_TIMEOUT to allow for longer HA sync times.

* iosxe/patterns
    * Modified want_continue pattern to match the prompt "Continue? [no]"


