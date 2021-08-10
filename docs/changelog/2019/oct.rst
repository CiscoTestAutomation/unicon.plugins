October 2019
============

October 29th
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.10


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
- core

  - Replace self.FLAG of spwan with self.has_buffer_left

  - Remove unnecessary Timeout log from setup_connection of BaseSingleRpConnection and BaseDualRpConnection

  - Add changes to correct truncation logic in add_state_pattern

  - Fix prompt recovery for connect/disconnect/connect scenario

  - Fix mock_device with SSH connections

  - Fix incorrect plugin selection for some scenarios

- generic plugin

  - Fix issue that receive service always fails after first receive attempt

  - Fix generic get_mode service

  - Change some service regex patterns to be looser on \s number

  - Enhance Execute and HaExecute to remove backspace and escape sequence in output

  - Enhance execute service to remove "--More--" in output

  - Fix copy service to raise exception when "No such file or directory" is reported

- nxos plugin

  - Add reload_creds to nxos and nxos/n5k plugins

- iosxr plugin

  - Add reload_creds to iosxr ncs5k plugin

  - Enhance spitfire plugin connect to look at ZTP lock and config lock to ensure
    initial connect does not fail right after reimage

  - Fix nxos HA connection to correctly handle "--More--" during connect stage

  - Add "logging console disable" into iosxr init configure command

  - Fix iosxr ask9k switchover service by changing STANDBY_STATE_REGEX

  - Enhance TraceroutePatterns for iosxr

- iosxe plugin

  - Fix iosxe HA execute to correctly handle "--More--"
