July 2025
==========

July 29 - Unicon.Plugins v25.7 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v25.7 
        ``unicon``, v25.7 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxr
    * switchover
            * Fixed timeout handling by using explicit timeout parameter instead of self.timeout.
    * Update monitor service prompt pattern
    * Increase monitor stop timeout
    * Update execute() service to exit unsupported modes (e.g. monitor mode)


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * Added support for 9500 and 9500x SVL switchover


