April 2025
==========

April 29 - Unicon.Plugins v25.4 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v25.4 
        ``unicon``, v25.4 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxr
    * Update admin host pattern
    * Update prompt commands to recover console

* generic
    * Updated output variable by passing count argument, To get get rid of messages like 'DeprecationWarning 'count' is passed as positional argument'
    * Update escape handler to support a list of prompt commands


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * Cat9k
        * Support for HA ROMMON
    * Added support for no enable password being set. A UniconAuthenticationError will be raised if the enable password is not set and the user tries to enable the device.

* generic
    * Return output of HAReloadService to match with generic ReloadService


