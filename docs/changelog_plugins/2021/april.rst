April 2021
==========

April 27th
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.4
        ``unicon``, v21.4

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

--------------------------------------------------------------------------------
                                      New
--------------------------------------------------------------------------------

* AIREOS PLUGIN
    * Add error_pattern for `^[Rr]Equest [Ff]Ailed And R'^(.*?) Already In Use`
    * Add error_pattern For `Wlan Identifier Is Invalid` and `^Request Failed`

* NXOS/ACI
    * Inherit services from nxos plugin

* GENERIC PLUGIN
    * Add syslog message handler to `connect`, `execute` and `configure` services

* IOSXE/CAT9K
    * Support `rommon()` and `reload()` services

* IOSXE
    * New exec error_pattern to match '% Bad IP address or host name% Unknown command or computer name, or unable to find computer address'
    * New configure error_pattern to match '% IP  routing table <name> does not exist'

* GENERIC EXECUTE AND CONFIGURE SERVICES
    * Added `append_error_pattern` argument

* NXOS
    * Added `skip_poap` statement for reload service
    * Add execute statement list for `execute` service
    * Add add error_pattern for "command failed...aborting"

* NXOS PLUGIN
    * Add dialog to handle commit confirm message
    * Use 'commit' as default commit command for `configure_dual` service


--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* NXOS/ACI
    * attach_console service for NXOS/ACI plugin

* IOSXR
    * Updated `run_prompt` pattern to accept more variety

* IOSXR/SPITFIRE
    * Fixed failed config handling when transitioning from config to enable state

* IOSXR/MOONSHINE
    * Updated shell prompt pattern

* AIREOS PLUGIN
    * Changed error_pattern `^(%\S*)?Error` To `^(%\S*)?(Error|error)` so it's case insensitive


* JUNOS PLUGIN
    * Update `configure` service to allow `commit_cmd` override

* IOSXE
    * Updated config prompt pattern to include "cloud"

* IOSXE/CSR1000V
    * Use IOSXE config prompt pattern

* GENERAL
    * Use plugin specific config prompt for config state transition
    * Enable 'service prompt config' if we detect no prompt on config transition

* SETUP.PY
    * Update version check to allow users to build local versions


