April 2026
==========

April 28 - Unicon.Plugins v26.4
-------------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.4
        ``unicon``, v26.4




Changelogs
^^^^^^^^^^

--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe/stack
    * StackSwitchover
        * Added state machine transitions to handle 'Press RETURN' and login prompts post-switchover
    * StackRommon
        * Fixed handling of mixed console states during rommon boot operations

* iosxe
    * pattern
        * Updated ``syslog_message_pattern``to recognize the trailing``key config-key password-encrypt`` master-key warning line so it is treated as banner/syslog noise instead of prompt content.
        * Updated ``disable_prompt``to avoid matching the master-key warning line ending in``<encryption-key>``, which could lead to incorrect hostname learning during login.
        * Added a regression unittest covering backend-style prompt matching for the master-key warning buffer.
    * Updated login credential handling for post-logout reconnects
        * Reuse the last successful device credential from ``current_credentials`` when reconnecting after logout
        * Added a cat9k unittest that reproduces console relogin after logout and verifies the device credential is reused instead of the terminal server credential
        * Updated cat9k mock data to include the initial terminal server password hop and the console banner before relogin


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe/ar1k/service_implementation.py
    * Added a new HA Reload implementation for ASR1k.


