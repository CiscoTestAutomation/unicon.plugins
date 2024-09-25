September 2024
==========

September 24 - Unicon v24.9 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.9 
        ``unicon``, v24.9 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* backend.spawn0
    * Modified RawSpawn
        * Added check for when a decode error occurs n amount of times

* unicon
    * topology
        * Fixed logic for proxy connection.
    * sshtunnel
        * Added -o EnableEscapeCommandline=yes to ssh-options.

* unicon.bases
    * Added message argument to log_service_call


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* generic
    * Added upwards error propagation for decode errors


