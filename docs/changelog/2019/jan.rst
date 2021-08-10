January 2019
============

Jan 31
------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

    ``unicon``, v3.4.7

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^

- Fixed a timeout related issue that was causing switchover service to fail.


Jan 23
------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

    ``unicon``, v3.4.6

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^

- New plugin: ACI

- Generic plugin

  - Update connect statements to handle setup prompts

  - press enter on 'kerberos no realm message' with username prompt

  - Added log_file service.

- Updated hostname learning to strip ansi escape codes from learned hostname

- Fix robot keyword error pattern handling in config keyword

- Added error pattern to linux plugin to catch 'No such file or directory' errors


Jan 21
------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

    ``unicon``, v3.4.5


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^

- Added package dependency that was missing from v3.4.4.


Jan 19
------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

    ``unicon``, v3.4.4


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^

- Added restore_state_pattern to state machine.

- Now generic copy service is only retrying in case of suspected bad
  network connection.

- Added support for replace and force parameter on xr config service.

- Added 'junos' to list of supported OS, created unit test to flag when
  the list of supported OS doesn't match the available plugin list.

- Added new generic services transmit / receive.

- Fixed a bug with password handling where enable and tacacs passwords were
  getting mixed

- Optimized log output to be more human friendly, indicating which device
  it's coming from

- Removed blinker package dependency

- Option to maintain initial state (mit) on connect

- XR plugin ping service now accepts vrf as input and passes it as part
  of the ping command (as opposed to the generic implementation which
  expects the device to prompt for vrf).

- Now SpawnInitError exception is raised if the spawn start command is
  not present and executable.

- Adapt the generic HA reload service to accept the reload_command parameter
  to align it with the simplex reload service.

- Add standby support for bash_console service

- Update ASA plugin to use generic connection statements, move init command to exec mode

- Password handling refactoring

- Playback functionality has been added. You can now record your device and
  save it to file. This allow to re-run script without having any device


