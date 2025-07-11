June 2025
==========

June 29 - Unicon v25.6 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v25.6 
        ``unicon``, v25.6 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* bases/connection
    * Added logout() method
        * Added logout implementation for routers


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon
    * Refactor plugin loading from pkg_resources.iter_entry_points to importlib.metadata.entry_points


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * Added support for fast reload pattern


