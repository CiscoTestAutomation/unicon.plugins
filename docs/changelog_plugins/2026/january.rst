January 2026
============

January 27 - Unicon v26.1  
-------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.1 
        ``unicon``, v26.1 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
Fix
--------------------------------------------------------------------------------

* generic
    * Update enable service to user transition dialog
    * Update escape_char_stmt to handle 2 check for buffer for connection refuse

* iosxe
    * Add Enable service to explicitly add "enable" command

* unicon.plugins
    * IOSXE/C9500/SVL_STACK
        * Add dis_state prompt statement  to stack_switchover_stmt_list preventing timeout when the standby comes up at disable mode.
    * IOSXE
        * updated the configure service logic to support the multiline banner

* iosxr
    * Updated the run_prompt regex to avoid mixing standalone # in execution output with enable prompt.


