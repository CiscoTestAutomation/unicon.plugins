August 2025
==========

August 23 - Unicon v25.8 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v25.8 
        ``unicon``, v25.8 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon/bases
    * router
        * Added a statement to logout dialog to handle the standby console locked
        * Added check in designate_handle to skip goto enable when standby is locked


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* cheetah
    * Added cheetah ap tokens in pids csv file

* iosxe/cat9k/9610
    * Added the support for stackwise virtual for c9610 devices
    * Added SVLStackReload and SVLStackSwitchover services


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* generic/patterns
    * Modified syslog_message_pattern to handle additional syslog message formats.


