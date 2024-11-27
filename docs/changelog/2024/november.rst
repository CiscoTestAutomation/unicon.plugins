November 2024
==========

November 26 - Unicon v24.11
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.11
        ``unicon``, v24.11




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon/bases
    * Router/connection_provider
        * Updated designate_handles to not change state of standby if it is locked.
        * Added quad device specific unlock_standby method to execute configs only on Active console


