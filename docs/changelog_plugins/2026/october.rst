October 2026
==========

October 27 - Unicon.Plugins v26.10
-----------------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.10
        ``unicon``, v26.10




Changelogs
^^^^^^^^^^

--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * Added ROMMON-only ``emgy:`` and ``emgy0:`` boot filesystems for IE3K and IE9K. Reload recovery prefers their ``.bin`` images, then the configured Clean recovery image, before applying the normal SSA, SPA, and generic BIN ordering to ``flash:`` and ``sdflash:``. Other IOS XE platforms retain their existing reload behavior.

--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe
    * IOS-XE execute and non-bulk configure commands now recover from corrupted terminal input by clearing it and retrying once. Bulk configuration does not support this recovery.
    * Added a cat9k regression test covering a post credential action that lands directly in enable mode before logout and relogin

* generic
    * Tighten learned-prompt matching for dollar and hash markers preceded by horizontal whitespace. Require a prompt-shaped prefix for these forms while retaining the existing handling for attached prompt markers.
    * Add regression coverage for chunked setup output, verifying a generated secret line is not classified as a prompt and the discard selection is sent before token discovery attempts to enable.
    * Fixed login failures when a username prompt immediately follows the Press RETURN to get started message.
    * Restored the active configuration submode branch before retrying a command after config-session lock recovery, including same-prompt context changes and hierarchical submodes multiple levels deep.
    * When Genie parsers are unavailable, automatic token discovery is skipped and connections use predefined testbed tokens.
    * Advance to the next ``cred_list`` credential after each password is sent, including when a terminal-server login lands directly at the device prompt without a post credential action
    * Recognize an unprefixed PnP HTTP-timeout line as asynchronous system output so Unicon can request a fresh prompt.
    * Run the existing settle-and-send handling when the asynchronous line is first matched, including when no additional console output follows.
    * Continue settling across multiple asynchronous chunks until a complete quiet interval is observed, bounded by an overall timeout.
    * Preserve the established deferred handling for other syslog messages so reload and switchover dialogs can process their own asynchronous output.
    * Keep the match independent of the PnP server URL and anchored to the start of the line to avoid matching ordinary command output.

* cheetah/ap
    * Updated the ping service to submit the default response for the AP sweep range prompt.
    * Updated the ping service to handle the AP data-pattern prompt and continue the interactive ping dialog.

* iosxe/cat8k
    * Treated ``image_to_boot`` as a ROMMON fallback during reload instead of forcing devices that autoboot normally to transition through ROMMON.

* iosxe/cat9k/c9350 stack
    * Complete reload dialog processing when a member reaches an enable prompt, avoiding a threading timeout after boot.

* ios
    * Isolated the token-discovery version test from the global LEARN_OS_VERSION environment override while preserving the full-version assertion.

* nxos/n9k
    * Handle the secure password standard question and admin password setup before generic login prompts. Suppress syslog-triggered returns only while the password setup sequence is active during connection or reload. Allow time for boot setup prompts after syslogs before recovering from a standalone boot syslog. The wait is configurable for N9K devices.

* ios-xe
    * StackWise Virtual connections and standby reset no longer depend on Genie utilities.
