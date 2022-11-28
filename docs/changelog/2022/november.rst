--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* router
    * Removed timeout_pattern in BaseServices
        * The timeout pattern was causing issues as it was getting matched for device output instead actual error pattern.

* connection
    * Modified logic for pattern detection of existing username
        * Previous pattern detection for username would match if username was used in the ProxyJump ssh option.


