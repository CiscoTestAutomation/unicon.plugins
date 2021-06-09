February 2021
============

February 23rd
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.2
        ``unicon``, v21.2


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

* Generic plugin
    * Add syslog message handler to connect, execute and configure services

* IOSXE/CAT9K
    * Support `rommon()` and `reload()` services

* Generic execute and configure services
    * Added `append_error_pattern` argument

* Aireos plugin
    * Add ERROR_PATTERN for ^[Rr]equest [Ff]ailed and r'^(.*?) already in use'
    * Add ERROR_PATTERN for r'WLAN Identifier is invalid' and r'^Request failed'
	
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* setup.py
    * Update version check to allow users to build local versions

* NXOS plugin
    * Add dialog to handle commit confirm message
    * Use 'commit' as default commit command for configure_dual service

* NXOS/ACI
    * Inherit services from NXOS plugin
    * attach_console service for nxos/aci plugin

* IOSXR/Moonshine
    * Updated shell prompt pattern

* Junos plugin
    * Update configure service, allow commit_cmd override

* IOSXE
    * Updated config prompt pattern to include "cloud"

* IOSXE/CSR1000V
    * Use IOSXE config prompt pattern

* Aireos plugin
	* Changed ERROR_PATTERN '^(%\s*)?Error' to '^(%\s*)?(Error|ERROR)' so it is case insensitive