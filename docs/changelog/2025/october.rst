October 2025
==========

October 28 - Unicon v25.10
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v25.10
        ``unicon``, v25.10




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon
    * Modified TestUniconSettings
        * Fixed regex pattern to correctly match Invalid input error message in exec command.

* plugins/linux
    * Updated unit tests to accommodate the removal of the default 'uptime' command from LINUX_INIT_EXEC_COMMANDS.

* adapters
    * Updated the log collection to check for runtime directory before moving

* modified basemultirpconnectionprovider
    * Updated token discovery to handle standby locked devices


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* unicon/bases/linux/connection
    * Added peripheral support for Linux OS devices
        * Updated BaseLinuxConnection to pass device to Spawn initialization, enabling clearing of busy console lines for Linux-based platforms


--------------------------------------------------------------------------------
                                      Add                                       
--------------------------------------------------------------------------------

* basemultirpconnection
    * Added swap_roles in Multi RP connection which is parent class to have it handled for other connections.


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe/cat9k/stackwise_virtual
    * Enhanced the designate handles for condition where a standby & b active


