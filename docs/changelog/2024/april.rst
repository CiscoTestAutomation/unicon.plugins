April 2024
==========

 - Unicon v24.4 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.4 
        ``unicon``, v24.4 

Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon.plugins
    bash$ pip install unicon

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon.plugins
    bash$ pip install --upgrade unicon

Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* sshutils
    * add_tunnel
        * add logic to handle allocating ports based on the tunnel type.

* unicon
    * Bases/Routers
        * Do learn hostname if only the learn pattern is in the statmachine patterns.
        * Update the connection init logic.
    * Patterns
        * Add Bad secrets to bad_passwords pattern.

* unicon/bases
    * Router/connection_provider
        * Update logic to not learn the hostname when the device is in shell mode.


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* unicon
    * Connection provider
        * Add args and kwargs for connect function


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * statemachine
        * add pki_hexmode state for iosxe

* iosxr
    * Added get_commit_cmd
        * Added support for 'commit best-effort' command.

* stackresetstandbyrp
    * Added iosxe/stack StackResetStandbyRP
        * iosxe/stack service reset_standby_rp
        * Check whole stack readiness to decide the result of reset_standby_rp


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxr/spitfire
    * Modified Prompt Recovery Commands
        * Updated prompt recovery commands to user CTRL+C.

* iosxe
    * connection provider
        * Get the pattern for the enable statment from state machine for handeling device prompts after

* resetstandbyrp
    * Modified generic ResetStandbyRP
        * Fixed to handle the optinal argument "reply"


