March 2021
==========

March 30th
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.3
        ``unicon``, v21.3

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
                                      Fix                                       
--------------------------------------------------------------------------------

* IOSXE/pattern
    * Allow 'WLC' to default prompt patterns

* Comware
    * Changed from `hp_comware` to `comware`

* IOSXE/CAT9K
    * image_to_boot argument support for reload service

* Generic
    * Add default error patterns to ERROR_PATTERN setting
    * Add default error patterns to CONFIGURE_ERROR_PATTERN setting

* IOSXE
    * Add bell char to enable prompt pattern

* Generic configure service
    * Fix config lock retry implementation
    * Allow exit, end, commit, abort commands to exit config state

* IOSXE/stack
    * Refactor switchover service

* NXOS
    * Update configure error patterns

* IOSXE/STACK
    * fix bash_console dialog

* statemachine
    * detect_state() now passes the connection context to go_to()


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* NXOS
    * Add 'mode' to configure() service as argument.
    * configure_dual service is now deprecated.
    * Fixed `switchto` and `switchback` service and added UTs

* FXOS/FP4K
    * New plugin for Firepower 4000 series

* FXOS/FP9K
    * New plugin for Firepower 9000 series

* ASA
    * New ASA plugin error pattern added to catch "Removing object-group (TEST_NETWORK) failed; it does not exist"


