October 2026
==========

October 27 - Unicon v26.10
----------------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.10
        ``unicon``, v26.10




Changelogs
^^^^^^^^^^

unicon
""""""
--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* unicon.sshutils
    * Modified SSHTunnel
        * Added support for binding SSH tunnels to the ``tunnel_ip`` configured in the testbed or passed to ``add_tunnel`` and ``remove_tunnel``.

--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* connection provider
    * Preserve explicitly selected credentials during in-place reconnects.
    * Use the device credential when a terminal-server connection reaches the device prompt before device authentication.
    * Retain the credential that authenticated when login tries multiple credentials.

* unicon.bases.routers.connection_provider
    * Fixed prompt matching after OS token learning redirects a connection, so shell command output ending in ``$`` is not mistaken for a device prompt.

unicon.plugins
""""""""""""""
--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* ios-xe cat9k c9800
    * Added IosXEc9800HAGroupConnection
        * Added ``chassis_type: ha_group`` support for physical and virtual C9800 wireless controller HA pairs.
