June 2025
==========

June 29 - Unicon.Plugins v25.6 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v25.6 
        ``unicon``, v25.6 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxr/spitfire
    * Update ZTP lock check

* unicon.plugins
    * IOSXE
        * Stack
            * Fixed `image_to_boot` parameter in reload service so that it is actually used in the reload process.

* generic
    * Update syslog pattern


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * IosXEPatterns
        * Added the ca-trustpool regex to match prompt for adding a CA certificate to the trustpool
    * Added ACM rules state and transition support to the IOS-XE plugin.
    * Enhanced Configure and HAConfigure services to support ACM rules CLI via the rules argument, using context-driven state transitions.
    * Added post-service transitions to gracefully return to enable mode after configuration.

* nxos
    * Introducing a new service l2rib_pycl in NXOS plugin as a replacement for the existing service l2rib_dt
    * Deprecating the existing service l2rib_dt


