July 2026
==========

July 28 - Unicon v26.7
----------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.7
        ``unicon``, v26.7




Changelogs
^^^^^^^^^^

unicon
""""""
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon.eal.dialog_processor
    * Modified SimpleDialogProcessor
        * Preserve Statement.matched_retries as dialog configuration and consume matched retry counts from processor-local state for each Dialog.process invocation.

* unicon.bases.routers
    * Modified BaseDualRpConnectionProvider
        * Added handling for the standby_locked state during dual RP handle designation.

* unicon.statemachine
    * Modified StateMachine
        * Initialize prompt_recovery to False before detect_state() can run before the first go_to().

unicon.plugins
""""""""""""""
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe
    * Modified Copy
        * Handle the Continue? [no]: prompt when copying running-config to startup-config.
