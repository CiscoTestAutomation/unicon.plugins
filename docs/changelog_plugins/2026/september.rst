September 2026
==============

September 29 - Unicon.Plugins v26.9
-----------------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.9
        ``unicon``, v26.9




Changelogs
^^^^^^^^^^

--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* fxos
    * Simplified the FTD console prompt pattern to reduce unnecessary regex repetition.

* iosv
    * Anchored ROMMON and shell prompt patterns.

* iosxe
    * Anchored stack ROMMON prompt patterns.
    * Stopped Cat4k connection initialization after replacement-dialog state detection.

* nxos
    * Anchored the module reload prompt pattern.
    * Stopped Nexus 7000 VDC discovery after state-detection-only connections.
    * Propagated NX-OS attach-console command failures immediately instead of allowing them to surface later as console-login timeouts.

* generic
    * Prevented the terminal-server ``Password OK`` statement from restarting the connection timeout when the device console remains silent.

* iosxe/cat8k
    * Added the ``C8300-1N1S-6T`` PID mapping so token discovery selects the CAT8K platform and C8300 model instead of the IOS XE software image name.

* aireos
    * Preserved replacement dialogs and state-detection-only behavior for dual-RP connections.

* iosxr
    * Stopped IOS XR connection initialization and state normalization after state-detection-only connections.

* cheetah
    * Updated ``pid_tokens.csv`` to identify Cisco Wireless CW91xx access points with the ``cheetah`` operating system and added current CW91xx PIDs.

* ios
    * Added default IOS OS version learning from ``show version`` for IOS, AP, and IOL connections without issuing a duplicate initialization command.

* iosxe/stack
    * Updated stack mocks to return console-specific show terminal output for active-handle designation tests.
    * Added regression coverage for reordered Active and Standby console connections while preserving Member handling.

* iosxe/cat9k/c9800/c9800_cl
    * Reorganized the virtual C9800-CL plugin under ``model: c9800`` and ``submodel: c9800_cl``.
    * Preserved common C9800 behavior through explicit connection and state-machine inheritance, with GRUB-specific behavior remaining in C9800-CL.
    * Updated ``C9800-CL-K9`` PID discovery to return ``model: c9800`` with ``submodel: c9800_cl``.
    * Updated the supported-platform and abstraction-token documentation for the new hierarchy.
    * Preserved platform, model, and PID abstraction during Bash parsing and included the device submodel when defined.
