July 2025
==========

July 29 - Unicon v25.7 
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

* bases/router
    * connection_provider
        * Updated logout service logic for single rp and multi rp connections

* router/connection
    * Initialized the UNICON_BACKEND_DECODE_ERROR_LIMIT to None for iosxr HA device connections


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* mock device
    * Add mock device for svl stack

* iosxe
    * Added cert-trustpool config pattern


