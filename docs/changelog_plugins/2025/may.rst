May 2025
==========

 - Unicon.Plugins v25.5 
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

* iosxe/cat9k/stackwise_virtual
    * Added support for SVL

* iosxe/cat9k/c9500x/stackwise_virtual
    * Added support for SVL

* generic
    * Add loghandler for subconnections to capture the buffer output


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* generic
    * Made it so incorrect login errors will attempt to use fallback credentials

* nxos
    * Add support for bash_console with module argument.
    * Make l2rib_dt_prompt pattern more strict


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* nxos
    * Added support for configure session
        * When using device.configure() you can now pass a session name with session="session_name"
            * IE device.configure("...", session="my_session")

* iosxe
    * IosXEPatterns
        * Updated the recovery-mode regex to match prompt for both mode
        * Added the rp-rec-mode regex to match prompt
    * Added acm state and transition support to IOS-XE plugin.
    * Enhanced Configure and HAConfigure services to support ACM CLI via acm_configlet argument using context-driven state transitions.
    * Added context-based transition function to enter ACM mode using acm configlet create <name>.
    * Added post-service transition to gracefully return to enable mode after configuration.


