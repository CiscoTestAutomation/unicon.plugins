April 2025
==========

April 29 - Unicon v25.4 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v25.4 
        ``unicon``, v25.4 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* connection
    * Added os learn version
    * Added ability to set learn_tokens and overwrite_testbed_tokens from a config file or environment variable
        * Environment Variables
            * UNICON_LEARN_TOKENS
            * UNICON_OVERWRITE_TESTBED_TOKENS
            * UNICON_LEARN_AND_OVERWRITE_TOKENS
        * Config File
            * [unicon]
                * learn_tokens
                * overwrite_testbed_tokens
                * learn_and_overwrite_tokens

* connection_provider
    * Modified update_os_version
        * Updated logic to execute 'show install summary' only on first connnection


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* linux
    * Modified linux connection provider
        * Wait for connection_timeout/2 on initial connection for the device to respond with some output

* generic
    * Add TRANSITION_WAIT setting to make transition wait time configurable


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* linux
    * Added support for prompt_line

* iosxe
    * IosXEPatterns
        * Updated the recovery-mode regex to match prompt

* iosxe_mock_data.yaml
    * Added 'show install summary' output in mock yaml


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * add test for learn os


