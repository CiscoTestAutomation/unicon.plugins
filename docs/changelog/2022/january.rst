--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* bases
    * Modified proxy connection
        * Added "proxy" to AssertionError message to make it more specific
        * Fixed Error when closing a non existent self.spawn
    * Modified proxy connection
        * Fixed connection error when recording device using proxy connections

* logs
    * Modified UniconFileHandler
        * Added specific handling of 'locale' encoding because of Python 3.10 changes to default encoding

* bases/routers
    * Modified BaseSingleRpConnectionProvider
        * Added option to invoke device token learning if learn_tokens connection option is set
    * Modified BaseMultiRpConnectionProvider
        * Added option to invoke device token learning if learn_tokens connection option is set

* connection provider
    * Added support for ROMMON init commands
    * Updated hostname learning for Dual RP


