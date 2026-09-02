August 2026
==========

August 25 - Unicon.Plugins v26.8
--------------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.8
        ``unicon``, v26.8




Changelogs
^^^^^^^^^^

--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe
    * Updated the shared single-RP and dual-RP syntax transition to use ``config check syntax`` so syntax checking works consistently on IOS XE and CAT9k HA devices.
    * Updated ``configure(config_syntax_check=True)`` and ``config_syntax()`` to enter syntax-check mode, validate the supplied commands, and return to enable mode.
    * Removed the obsolete ``syntax_configlet`` handling and unregistered ``Syntaxsh`` service.
    * Modified state machine
        * Answer the uncommitted changes prompt when leaving configuration mode on controller-managed single- and dual-RP devices.
    * Updated CAT8K reload-to-ROMMON handling to recognize ``System Bootstrap`` output.
    * Saves the environment when prompted and sends Ctrl-C at the boot interruption point.
    * Added the ``C8300-2N2S-4T2X`` PID mapping for CAT8K C8300 plugin selection.
    * Fixed ROMMON boot dialogs to invoke wrapped statement callbacks according to their declared parameters.
    * Copied generic connection statements before applying IOS XE-specific callback wrapping.
    * Updated the configure service to automatically answer the interactive RSA key modulus prompt with 2048 bits while allowing a caller-provided reply to override the default.
    * Added regression and mock-device coverage to verify RSA key generation completes without a caller-provided dialog.

* iosxe/stack
    * Modified init_standby
        * Added STACK_STANDBY_CONSOLE_ATTACH setting, off by default. Enable it on stacks where every console connects to the active RP.
        * Verify which console is on the standby RP using the '*' row of 'show switch' instead of assuming the designated standby handle.
        * Attach to the standby RP console when no console reaches it, so device.standby, target='standby' and swap_roles() no longer operate on the active RP without reporting an error.
        * Release a console attach left over from an earlier run before probing, so a stale attach is not mistaken for a real standby.
    * Modified disconnect
        * Detach the standby RP console so the next connect is not refused with 'Address already in use'.
    * Modified set_init_commands
        * Skip 'show version' on an attached standby console, whose output is rate limited and times out the connect.
    * Added stack-specific reload handling for the transition from ``Press RETURN`` to an authentication prompt. The stack reload dialog now avoids an empty username and completes authentication in the same dialog flow.

* generic
    * Updated the syslog message pattern to match ``UNIX ERR:tcgetattr:Inappropriate ioctl for device`` output so it is handled as ignorable syslog noise.
    * Modified connection_refused_handler
        * Propagate a typed ``ConnectionRefusedError`` to Unicon core instead of clearing terminal lines and reconnecting recursively from a connection dialog callback.
        * Removed the plugin-owned ``CONNECTION_REFUSED_MAX_COUNT`` default; it is now defined alongside the retry logic in Unicon core.
