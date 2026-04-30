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

* unicon/patterns
    * Update connection refused pattern to include "Requested line is busy!"

* routers/connection_providers
    * connect
        * Unwrap connection kwargs and assign to device object for the arguments to be used by underlying connection providers.

* bases/router/connection_provider
    * Use enable service to transition to enable mode


--------------------------------------------------------------------------------
Add
--------------------------------------------------------------------------------

* nxos/n9kv
    * Added AttachModuleConsoleN9k service to attach to module console of N9K devices.


--------------------------------------------------------------------------------
New
--------------------------------------------------------------------------------

* iosxe/c8kv/statemachine
    * Added IosXEC8kvSingleRpStateMachine and IosXEC8kvDualRpStateMachine
        * Added new state machine for C8KV devices to support boot statement

* iosxe/cat9k/c9350/stack
    * Added the support for stack for c9350 devices
    * Added C9350StackReload service


--------------------------------------------------------------------------------
Recovery.
--------------------------------------------------------------------------------

* iosxe/c8kv/statements
    * Added boot_image statement for C8KV devices
        * Modified the statement to support C8KV grub> mode by adding send(cmd)


--------------------------------------------------------------------------------
Fix
--------------------------------------------------------------------------------

* pid_tokens
    * Updated proper platform/model for IR1101 devices.

* generic/service_pattern
    * Modified ping validate pattern to match the "Validate reply data? [no]" prompt correctly in generic patterns.

* generic/service_implementation
    * enable
        * Updated UniconAuthenticationError and CredentialsExhaustedError as exceptions as they were wrapped inside the subcommand failure for a failing UT.

* iosxe/patterns
    * Updated enable_prompt regex patterns to include 'eWLC' and allow alphanumeric characters in the device identifier section.

* generic/statemachine
    * Fixed config transition retry handling to avoid resending configure terminal when configuration mode is already entered.


