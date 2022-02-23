--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* routers/connection provider
    * Updates to allow hostname learning when device is found in config mode

* bases
    * Modified BaseCommonRpConnectionProvider
        * Added shared implementation of learn_tokens method to reduce duplicate code
    * Modified BaseSingleRpConnectionProvider
        * Remove duplicate code from learn_tokens
    * Modified BaseMultiRpConnectionProvider
        * Remove duplicate code from learn_tokens


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* statemachine
    * add_path
        * add index to identify where to add the new path in self.paths
    * add_state
        * add index to identify where to add the new state in self.states


