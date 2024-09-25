September 2024
==========

September 24 - Unicon.Plugins v24.9 
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

* iosxr
    * Added support for APIC patterns

* iosxe
    * Update config prompt pattern to support CA cert map

* generic
    * Update execute() service log message to include device alias
    * Add parse method to bash_console context manager with abstraction fallback to linux os


--------------------------------------------------------------------------------
                                      Add                                       
--------------------------------------------------------------------------------

* apic plugin
    * Added Regex in post_service in Execute to remove extra junk values.


