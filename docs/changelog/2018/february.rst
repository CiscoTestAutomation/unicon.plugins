February 2018
=============

February 12 - v3.0.1
--------------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v3.0.1


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Linux connection and plugin updates

    - Added ping service

    - Added learn hostname feature

      Linux connections now support the `learn_hostname` connect option to
      automatically learn the hostname.

      This improves reliable prompt matching as the default prompt matching may
      result in false positives when the command output contains one of the
      prompt pattern characters `> # % ~ $` at the end of a line.

    - Prompt stripping update

      Only the last matching prompt is stripped from the output.
      When using the default prompt, false prompt matches may strip
      parts of the output instead of the prompt.

    - Updated unittests

      The linux plugin unittests now cover about a dozen known prompts
      to validate prompt pattern matching and hostname learning.


- iosxr plugin updates:

  - Fixed bug in iosxr and iosxr/iosxrv plugins that was causing incorrect
    output from device.execute.

  - Update to Moonshine plugin:
    Make the prompt regex be more restrictive, by using the regex enforced in
    XR command files.


- nxos plugin updates:

  - HA reload service now rediscovers active/standby roles
    to accommodate targets that may switch roles after reload.


- Core features

  - Updated plugin discovery mechanism to support external plugin packages.

  - Removed OS static checking list, and made a warning instead.

  - New feature that allows user to specify initial exec and config command
    when connecting to a device.  Users can now specify `init_exec_commands`
    and `init_config_commands` options when connecting to a device.

  - The terminal variable is now set to VT100 before launching the telnet or
    ssh connection to a device. This is to tell devices not to use fancy ANSI
    escape characters (e.g. colors) in the prompt. The escape characters
    conflict with the (Linux) learn_hostname feature.

  - Removed os.sync from send method as this was causing hung sessions
    on some platforms.


- Testing related features

  - Added mock_device_cli console script to run mock device as
    a standalone program.


