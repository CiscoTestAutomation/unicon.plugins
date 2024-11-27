November 2024
==========

November 26 - Unicon.Plugins v24.11
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

* iosxe
    * Added UT for Quad device to test scenario when standby console is disabled

* iosxr
    * SPITFIRE plugin
        * Added UNICON_BACKEND_DECODE_ERROR_LIMIT with a default value of 10, to handle scenarios when the device is slow

* hvrp
    * Update config pattern
    * Update configure service to handle immediate vs two-stage config mode

* nxos
    * modify regex to handle new error pattern for NXOS

* generic
    * Modified enable_secret regex pattern to accommodate various outputs
    * Updated password_handler to pass password if password key in context dict


--------------------------------------------------------------------------------
                                      Add                                       
--------------------------------------------------------------------------------

* iosxe
    * Update prompt recovery command


