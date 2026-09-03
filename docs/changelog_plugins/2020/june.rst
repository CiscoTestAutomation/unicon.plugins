June 2020
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v20.6


Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon.plugins


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon.plugins


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

* Fixed ambiguous python shebang in mock devices
* Updated generic configure pattern to include ca-trustpoint

* [IOSXE] Added recovery-mode support
* [IOSXE] Updated shell pattern

* [IOSXR] Added commit retry timer that can be controlled under settings in the testbed yaml file
* [IOSXR] Updated admin_config prompt
* [IOSXR] Fixed enable pattern

* [AIREOS] Added Invalid error_patterns
* [AIREOS] Enhanced reload pattern
* [AIREOS] Fixed HA execute service to use service dialogs
* [AIREOS/IOS] Added logging console disable to INIT_EXEC_COMMANDS

* [JUNOS] Enhanced plugin to fail on commit failures
* [JUNOS] Updated CONFIGURE_ERROR_PATTERN in setting

* [STAROS] Updated error patterns and exec init commands

* [LINUX] Updated single hash prompt pattern

* [NXOS] Fixed switchover timeout hard code issue

* [CIMC] Update CIMC prompt pattern
