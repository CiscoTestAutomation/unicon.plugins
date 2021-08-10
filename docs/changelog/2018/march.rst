March 2018
==========

March 9 - v3.0.2
----------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v3.0.2


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Generic plugin updates

  - Fixed a hang observed on initial telnet connection.

- Linux plugin updates

  - Bug fix to the learn_hostname feature.

- Core bug fixes

  - Fixed a bug in spawn.expect, now users may inspect which pattern in
    a list matched the output, bringing the feature into alignment with
    dialog.process.

  - Fixed a bug in the addplugin helper.

  - Plugins can set the TERM attribute to set the TERM environment variable.
    Some plugins require this setting in order to ignore ANSI escape sequences
    coming from the device.


March 27 - v3.0.3
-----------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v3.0.3


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Linux plugin update

  - new NXOS subcommand for attaching to consoles on linecards

  - new NXOS subcommand for attaching to bash shell using context managers

- CIMC plugin update
    Add response for `Enter 'yes' or 'no' to confirm` pattern

- New feature: CLI proxy
    This feature allows users to connect to devices via another device.

- Updates to VOS plugin
    regex pattern updates
    support for Continue (y/n) prompt
    set pagination to off by default
