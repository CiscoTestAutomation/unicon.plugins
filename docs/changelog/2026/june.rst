June 2026
==========

June 30 - Unicon v26.6 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.6 
        ``unicon``, v26.6 




Changelogs
^^^^^^^^^^--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon
    * logs
        * Set the pyATS tasklog adapter level to INFO to prevent debug records from being emitted to the tasklog.
    * connection_provider
        * Fixed credential storage logic to properly handle multi-credential login_creds lists.
    * Modified BaseStackRpConnectionProvider
        * Connected stack subconnections in parallel during stack establish_connection.
        * Parallelized ROMMON init and boot handling for targeted stack subconnections.
        * Reported per-alias failures and verified targeted subconnections exit ROMMON before handle designation.
        * Preserved distinct child connection log files during parallel stack connect and boot flows.


