August 2026
==========

August 25 - Unicon v26.8
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.8
        ``unicon``, v26.8




Changelogs
^^^^^^^^^^

unicon
""""""
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon.bases.connection
    * Modified Connection connect
        * Clear stale previous_credential on the target context before the proxy/non-proxy branch so proxy_connections reconnects also restart credential selection from the first login_creds entry.
    * Modified Connection proxy_connect
        * Clear stale previous_credential on each proxy hop before its connection provider runs, so every hop of a multi-hop proxy chain restarts credential selection. Only hop 0 goes through setup_connection(); hops 1 and beyond are connected directly and previously retained relogin state from a prior session.
    * Added Connection reset_previous_credential
        * Helper that clears previous_credential on a connection and its subconnections.

* unicon.bases.routers.connection
    * Modified BaseSingleRpConnection and BaseMultiRpConnection setup_connection
        * Clear stale previous_credential (parent and subconnection contexts) at the fresh-spawn boundary so every reconnect restarts credential selection from the first login_creds entry (e.g. terminal server), even for plugins that override disconnect() (hvrp, gaia, fxos/ftd).

* unicon.bases.routers.connection_provider
    * Modified BaseSingleRpConnectionProvider establish_connection
        * Store the credential that actually answered the most recent password prompt as current_credentials, so a terminal-server post action that reaches the device prompt before later login_creds entries are consumed selects the correct credential.
    * Modified disconnect cleanup
        * Ensured all spawns are closed when sending the exit command fails.

* unicon.bases
    * Modified Connection, BaseMultiRpConnection, and BaseStackRpConnectionProvider
        * Moved clear-console retries outside connection dialog callbacks so simultaneous stack member refusals are recovered once and retried from a fresh set of spawns.
        * Avoided a redundant second stack state detection after a member has already reached a valid non-disable prompt.
        * Preserved the second detection for disable prompts that may actually represent a standby-locked stack member.
        * Moved the ``CONNECTION_REFUSED_MAX_COUNT`` default into core settings with the retry logic that consumes it.
        * Preserved the originating device for proxy connection refusals so recovery never clears an unrelated target console.
        * Preserved the originating proxy device while setting up multi-RP subconnections.
        * Preserved the final target device when a refusal occurs after connecting through a proxy.
    * Modified connection cleanup
        * Prevented failed connections and reconnects from retaining stale PTY-backed spawns.
        * Removed temporary connection log handlers after successful and failed connection attempts.

* unicon.eal.backend.pty_backend
    * Modified Spawn close
        * Made PTY cleanup idempotent and added bounded child-process reaping.
