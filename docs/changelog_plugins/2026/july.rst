July 2026
==========

July 28 - Unicon.Plugins v26.7
------------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.7
        ``unicon``, v26.7




Changelogs
^^^^^^^^^^

--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe/settings.py
    * Added a new password error pattern to handle cases where the password is against policy.

--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* generic
    * Modified get_enable_credential_password
        * When a terminal-server post action reaches the device prompt before the final login_creds entry is consumed, prefer the configured login/fallback credentials for the enable secret instead of the generic enable lookup, which otherwise sends the wrong password to the enable prompt.
    * Fixed ``default_hostname_pattern`` to capture the full hostname token when it starts with a keyword (e.g. ``Switch-C9200L-24T-4X-JAE2248059H`` was incorrectly learned as just ``Switch``). This caused stack/HA ``unlock_standby`` to fail because ``%N`` was set to the truncated keyword, making the disable prompt unrecognizable on the standby console.
    * Updated the ``enter_your_selection_2`` pattern to use whole-buffer match mode so that the selection prompt is correctly handled even when syslog messages such as ``Autoinstall trying`` appear on the line immediately following the prompt.
    * Added configure_yes_no_stmt to configure_statement_list to handle interactive [yes/no]: (slash variant) prompts during device.configure() calls. Sends 'yes' to allow commands such as 'no key config-key password-encrypt' to complete without timing out. The [yes,no] comma variant is intentionally excluded to avoid interfering with existing platform-specific confirmation dialogs.
    * Modified HAReloadService
        * Wait for the boot messages to settle (POST_RELOAD_WAIT / buffer_settled) after reload before logging in, mirroring the single-RP Reload path.

* iosxe/cat9k
    * stackwise_virtual
        * Updated SVL handle designation to execute ``show switch`` with prompt-match retries and parse the collected output, preventing a fake ``Switch#`` prompt in command output from truncating stack information.

* iosxe
    * Added ``ROMMON_DIR_TIMEOUT`` setting (default 120s) and applied it to the rommon ``dir <fs>`` listing in ``boot_image``, so a cluttered bootflash no longer trips the default expect timeout and raises ``TimeoutError`` while discovering boot images from rommon.
    * Added ``continue_yes`` pattern and statement to handle ``Continue? [yes]:`` prompt when configuring ``vrf`` under ``ipv6 dhcp pool`` context.
    * Updated enable and disable prompt matching, and default-hostname learning, to recognize lowercase ``router`` during controller-mode transitions.
    * stack
        * Added regression coverage for stack reload dialogs that reuse generic reload statements with matched retry configuration across stack subconnections.
    * cat9k
        * c9800
            * Added GRUB-aware ``rommon -> disable`` state machine path and ``statements.py``.

* iosxe/stack
    * Fixed stack reload post-discovery handling to prevent an extra blank return from causing an out-of-phase login prompt.
