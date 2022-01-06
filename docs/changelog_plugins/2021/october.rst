--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* nxos
    * Modified copy service
        * Fixed to handle source_file properly

* iosxe
    * Refactored rommon state transition, reload and rommon services

* generic
    * Added buffer_wait statement and refactored chatty_term_wait code
    * Added wait to config transition to avoid false negatives in config transition
    * Add match for unconfigured WLC to default hostname pattern


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe/cat9k
    * Added support for container shell


