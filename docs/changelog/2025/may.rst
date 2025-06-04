May 2025
==========

 - Unicon v25.5 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v25.5 
        ``unicon``, v25.5 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Add                                       
--------------------------------------------------------------------------------

* connection provider
    * moved the logic of boot_device to a separate function before designating handles
    * added the init_active to handle the learn_hostname instead of having it in designate handles
    * Store "current_credentials" under device.credentials when credentials are used

* connection
    * Added logging per subconnection for DualRp, Stack and Quad connection


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* generic
    * service implementation
        * Update the state for debug mode in attach service.


