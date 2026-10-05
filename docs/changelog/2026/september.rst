September 2026
==============

September 29 - Unicon v26.9
---------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.9
        ``unicon``, v26.9




Changelogs
^^^^^^^^^^

unicon
""""""
--------------------------------------------------------------------------------
                                      New
--------------------------------------------------------------------------------

* unicon.core.pluginmanager
    * Added generic support for optional submodel-aware plugin registration and selection for devices that define a submodel.
    * Added fallback to the model plugin when a matching submodel plugin is unavailable.

* unicon.adapters.topology
    * Added forwarding of an optional device submodel to the Unicon connection factory.

* c9800-cl
    * Uses ``model=c9800`` with ``submodel=c9800_cl`` and falls back to the C9800 model plugin when a matching submodel plugin is unavailable.

* unicon.bases.connection
    * Modified Connection
        * Added optional connection_dialog to connect() so callers can provide a replacement dialog for initial state detection and break-boot recovery. Existing behavior is unchanged when it is omitted.
        * Added optional skip_initialization to connect() so callers can stop after initial state detection without hostname learning, token learning, or normal connection initialization.

* unicon.bases.linux.connection_provider
    * Modified BaseLinuxConnectionProvider
        * Added replacement-dialog and skip_initialization handling while preserving existing behavior when omitted.

* unicon.bases.routers.connection_provider
    * Modified RP connection providers
        * Added replacement-dialog handling across single-RP, dual-RP, stack/SVL, and quad-RP connections while preserving normal connection behavior when no replacement is supplied.

--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* unicon.eal.backend.pty_backend
    * Raise typed ``EOF`` errors for closed or failed PTY spawns instead of exposing low-level ``select`` errors.
    * Safely clean up failed PTY sessions without unnecessary disconnect delays, while preserving subprocess exit output for connection-failure dialogs.
    * Add PTY child-liveness detection so recovery can distinguish exited sessions from live shared or inherited sessions.
    * Modified Spawn.close
        * Terminate a spawned process that is still running but is not a child of the closing process. os.waitpid() raises ECHILD in that case, which was treated as "already exited", leaving telnet/ssh sessions alive and holding terminal server console ports after disconnect()/destroy().

* unicon.statemachine
    * Modified StateMachine add_state
        * Propagate the hostname learning pattern to newly added states so enabling hostname learning does not generate patterns containing ``None``.

* unicon.bases.routers.connection_provider
    * Modified BaseStackRpConnectionProvider designate_handles
        * Identify the active stack handle from terminal line 0 when console and switch order differ.
        * Preserve existing standby and member handle behavior.

unicon.plugins
""""""""""""""
--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* generic plugin
    * Modified enable credential selection
        * Prefer an explicitly configured enable credential over fallback login passwords when a terminal-server post action reaches the device prompt.
        * When no explicit enable credential exists, use the login credential that actually reached the device prompt instead of blindly selecting the first bad-password fallback credential.
    * Modified enable authentication failure handling
        * Raise ``UniconAuthenticationError`` when a device rejects an enable password, allowing callers such as Genie Clean to select their authentication-recovery path.
        * Preserve login fallback credential behavior for login authentication failures.

* ios xr
    * Modified initial connection recovery to discard uncommitted changes and clear an SDR running-configuration inconsistency from exec mode.
    * Kept essential-ops mode separate from SDR inconsistency recovery.

* unicon.plugins.confd
    * Modified ConfdConnectionProvider init_handle
        * Learn a runtime hostname before executing initialization commands.

* unicon.plugins.sdwan.viptela
    * Modified ViptelaPatterns
        * Recognize runtime vSmart hostnames and distinguish exec prompts from configuration prompts.

* iosxr
    * Modified Configure
        * Retry complete configuration transactions when a running-configuration lock blocks commit.
        * Report the active lock details when the retry limit is reached.
