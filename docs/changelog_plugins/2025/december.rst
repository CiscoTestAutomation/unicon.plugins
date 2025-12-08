December 2025
==========

December 30 - Unicon.Plugins v25.11
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v25.11
        ``unicon``, v25.11




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe
    * Added cursor position handling in bash ContextMgr to prevent delays during shell initialization.

* nxos
    * Updated the LC bash prompt pattern to include an anchor and improve prompt detection performance.

* generic
    * Updated syslog pattern to handle insecure dynamic warning message for SSH hostkey with insufficient key length.

* linux
    * Updated prompt patterns to better handle ANSI escape sequences in prompts


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* generic/settings.py
    * Updated the temporary enable secret to include a special character.


