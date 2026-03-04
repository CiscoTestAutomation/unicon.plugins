February 2026
==========

February 24 - Unicon v26.2 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.2 
        ``unicon``, v26.2 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* mock_device
    * Fix asyncio deprecation warning for python 3.14

* routers.connection_provider
    * Added logic to merge settings dict instead of replacing Settings object
    * When settings dict is passed to connect(), it now properly updates existing Settings object using update() method


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* stackwisevirtualconnectionprovider
    * Avoid traceback on empty 'show switch' output

* unicon.plugin/cat8k
    * Modified the Switchover implementaion of cat8k to connect post switchover
    * This is to avoid any prompt mismatch issues post switchover

* generic/statements
    * Modified terminal_position_handler
        * Changed terminal position response to \x1b[0;0R

* generic/service_pattern
    * Modified ping verbose regex patterns for verbose prompts to correctly match the prompt.


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* linux
    * Modified LinuxPatterns
        * Add support for linux prompt (server.cisco.com)~


