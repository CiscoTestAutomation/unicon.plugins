June 2026
==========

June 30 - Unicon.Plugins v26.6 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.6 
        ``unicon``, v26.6 




Changelogs
^^^^^^^^^^--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe
    * Added stack ``Applying config on Switch N`` pattern to syslog handling so
    * cat9kv
        * Added CAT9KV-specific GRUB boot handling

* generic
    * Updated configure service so that the post_lines processing now recursively detects and
    * Added an error log when connection refused handling reaches

* iosxe/cat9k
    * Fixed ``HAReloadService.pre_service`` iterating ``_subconnections`` dict

* apic
    * Updated shell prompt pattern to handle both CentOS-style ([root@host dir]#) and Ubuntu-style (root@host~#) prompts

* iosxr/spitfire
    * SpitfireSingleRpConnectionProvider
        * Updated show ztp log command include filter to use double quotes to match the new IOSXR include behavior.


