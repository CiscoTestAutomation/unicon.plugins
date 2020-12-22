May 2019
========

May 28th
--------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.5.0


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- iosxr plugin

  - Enhance following patterns to support different versions of iosxr:
    run_prompt, admin_prompt, admin_conf_prompt, admin_run_prompt

  - Fixed admin_attach_console on iosxr plugin, it now exits correctly.

- Update user guide to remove prompt argument from bash_console service

- Added ASA plugin error pattern.

- Generic plugin

  - The generic switchover service now respects the timeout parameter.

  - Added retries option to the generic HA config service.

  - Now ensuring device is brought back to ``enable`` state after
    reload or switchover.

- Core changes

  - Enhance RawSpawn expect, add argument "log_timeout" to control
    whether log Timeout info

- Introducing iosxe/sdwan plugin with config commit support.



May 8th
-------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.4.1


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Added return_output option to the reload service of the generic, nxos and
  iosxe/cat3k plugins, now allowing reload output to be returned.
