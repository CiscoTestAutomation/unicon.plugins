October 2024
==========

October 29 - Unicon.Plugins v24.10
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.10
        ``unicon``, v24.10




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* pid tokens
    * Updated PID tokens to support NCS devices


--------------------------------------------------------------------------------
                                      Add                                       
--------------------------------------------------------------------------------

* apic plugin
    * Modified the regex patterns in the post_service method in Execute to remove extra junk values and retain the newline character in the output.
    * Added a configure class to eliminate extra junk values from the output.


