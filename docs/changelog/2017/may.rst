May 2017
========


May 8 - v2.3.0
--------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.3.0


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

The following changes were introduced as a result of uniclean
IOSXE plugin development:

- Added IOSXE simplex plugin

  - Pulled up common functionality from iosxe/cat3k plugin to iosxe layer.

  - Added rommon->disable transition logic.

- Added IOSXE HA plugin

  - Enhanced generic enable/disable prompt patterns to support
    IOSXE standby RP prompt.

  - Now properly detecting standby locked state.

  - Pushed down HA role detection logic to generic and nxos plugin layer from
    unicon core.

- Changes to iosxe/cat3k plugin

  - Now throwing exception if a cyclic bootloader reboot loop is detected.

- Changes to generic plugin

  - Added retry / max_attempts to generic copy service to allow retries when
    uniclean image copy fails, this will help build resilience against
    sporadic network issues.

  - Added a new prompt removal algorithm to the generic Execute service
    (both simplex and HA)

- Extended the iosxe/cat3k Reload service with a connection locked detection
  and wait loop to ensure a stack with a standby peer comes up correctly

- Enhanced EAL/Pty layer to:

  - perform a graceful shutdown when closing the spawn session.

  - perform a post-shutdown wait to ensure "Connection Refused" is not seen
    if a back-to-back disconnect/reconnect is done.

- Enhanced Settings base class to allow it to be multiply inherited by
  uniclean settings object.

- Enhanced expect logs to include target and match groups for easier debugging.

- Added baseline support for mocked devices.

- Added enable_vdc statement to the simplex N7K nxos reload statement list.

- Various bug fixes arising from Genie integration.

- Addition of xrutconnect protocol support for Moonshine
