Sept 2018
=========

Sept 5 - v3.3.0
---------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

    ``unicon``, v3.3.0


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- NXOS plugin fix:
   Fixed broken ping6 service for HA NXOS connection.

- Username and password details can now be specified per connnection.

- Plugin update for IOS-XR/NCS5K
    Added reload service for NCS5K devices

- CLI proxy bugfix
    List of commands was only executing the last command

- XR pattern fixes

- Ignore chatty terminal output in generic execute service
    settings.IGNORE_CHATTY_TERM_OUTPUT is to True to ignore previous terminal output
    before executing commands.

- CLI proxy bugfix
    List of commands was only executing the last command

- Learn hostname default pattern update
    execute() now returns output when default hostnames like Switch or Router are used

- ASA plugin updates
    Basic unittest for ASA plugin
    Pattern update to account for priority and state in prompt
    Settings inheritance from generic settings

- CLI proxy bugfix
    List of commands was only executing the last command

- IOS-XR plugin updates
    Added switchover service
    execute service fixes
    admin execute fixes
    Add 'xr' as a possible prompt, as it is the default for spitfire
    Improve failed config handling
    Add a grouping to match everything before the prompt to the moonshine patterns
    Make the XR prompt matching more restrictive
    XRv launch wait updates using dialogs

- Fix bug preventing passing the logfile argument

- AireOS plugin update
    Bugfix for error pattern setting
    Unittest for AireOS plugin

- NXOS plugin fix shell prompt pattern
