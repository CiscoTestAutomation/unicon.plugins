September 2017
==============

September 18 - v2.3.5
---------------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.3.5


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- New plugin: ConfD with support for NSO, ESC and NFVIS

- Update to nxos plugin to support ``shellexec`` on non-MDS platforms.

- Handle SSH ``continue connecting`` in generic and IOSXR plugin.

- Added ``%`` to linux prompt pattern.

- NSO plugin updates

    - Added ``error_pattern`` option to NSO plugin services

        - Updated implementation for execute, configure and command
          services to allow ``error_pattern`` option to be specified.

        - Update documentation with examples of error_patterns.

    - Fixed bugs in command stripping and timeout handling

    - Updated unittests

        - Added tests with list of commands for configure and execute services

        - Changed NsoConnection to Connection class.

        - Changed the assertion statements to use unittest assertion methods.

        - Added unittests for passing ``error_pattern`` options.

    - Documentation update

        Added example execute service with list of commands.

    - Changes in ``execute`` service: maintain CLI style, change in output
      stripping.

        When you execute a command using the ``execute`` service, the style
        that is active before execution is restored at the end of the
        execution.

        This means that you cannot use the ``execute`` service to switch styles,
        use the ``cli_style`` service to change CLI style.

        Executing the command ``switch cli`` raises an exception and
        point to cli_style.

        The output is stripped of whitespace from the right only,
        if a CR/LF is present at the start of the output it is stripped.
        Previously, whitespace was stripped from both sides of the output text.

- iosxe and iosxe/cat3k plugin updates:

    - Adapted patterns to be more real-time efficient to better handle long
      outputs.

    - Introduced mocked device tests for ASR HA, ISR and CAT3k.

    - Fixed the switchover service so it works properly for ASR HA.
