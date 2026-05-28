May 2026
==========

May 26 - Unicon v26.5
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v26.5 
        ``unicon``, v26.5 




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* nxos/n9k
    * AttachModuleConsoleN9k
        * Updated to use 'run bash sudo rlogin lc<N>' command for CTC collection support

* nxos
    * AttachModuleConsole
        * Updated escape character detection to match 'press ~, to exit' message

* iosxe
    * Added self-signed secure server certificate warning messages to syslog
    * Updated fast_reload_confirm  in pattern to match Proceed with fast reload? [confirm].
    * Modified c8kv statemachine
        * Updated rommon handling and state transitions
        * Cleaned up unused code and improved state management
    * Modified c8kv statements
        * Updated statements for better rommon support
    * Modified patterns
        * Updated patterns to support c8kv rommon handling
    * Modified statements
        * Updated general statements for improved rommon compatibility
    * Modified patterns
        * Updated are_you_sure pattern to make [y] optional, fixing TimeoutError
    * Connection provider
        * Updated enable invocation to use the connection-level

* iosxr
    * Modified execute service
        * Fixed state detection overrides so commands that disable detection do not affect later execute calls.
        * Passed the per-command detect_state value through service kwargs instead of storing it on the service instance.

* cheetah/ap
    * Updated the AP shell prompt pattern to match both ``~`` and ``/`` shell prompts, and added a regression test for the home-directory prompt case.

* unicon.plugins
    * Updated the pid_tokens.csv file to include additional pids.

* generic
    * Enable
        * Added support for passing `prompt_recovery` to the state machine when


--------------------------------------------------------------------------------
                                    Prompt.                                     
--------------------------------------------------------------------------------


