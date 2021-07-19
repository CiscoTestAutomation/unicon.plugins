July 2019
=========

July 31st
---------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.7.2


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Updated linux prompt pattern to handle additional cases.
- Updated pattern failures seen on device connection.


July 30th
---------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.7


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
- core

  - fix StateTransition do_transitions to return correct output

  - fix dialogs with multi thread to send command to correct connection

  - inherit base Connection from Lockable and add RLock for BaseService

  - improve performance by enhancing pty_backend to support different modes in match_buffer.
    By default, match_mode_detect is enabled. Detect rules are as below:

    - search whole buffer with re.DOTALL if:

      - pattern contains any of: \\r, \\n

      - pattern equals to any of: .*, ^.*$, .*$, ^.*, .+, ^.+$, .+$, ^.+

    - Else if pattern ends with $, will only match last line

    - In other situations, search whole buffer with re.DOTALL

  - improve performance by compiling regex patterns first in dialog_processor

  - improve performance by removing re.search again in truncate_trailing_prompt

  - add connection "host" in SSHTunnel and topology adapter


- added credential support

  - When pyATS integration is used,

    - If a ``default`` credential is supplied, then a credential of any other
      name is looked up explicitly and is not found, the ``default`` credential
      is used instead.

    - credentials supplied to the connection contain any credentials defined
      at the device and testbed levels as well.

  - If one or more credentials are supplied:

    - The ``tacacs`` and ``passwords`` pyATS testbed keys are ignored.

    - Use of any of the following `unicon.Unicon.Connection` arguments cause a
      deprecation warning to be raised :

      - ``username``
      - ``password``
      - ``enable_password``
      - ``tacacs_password``
      - ``line_password``

    - The following credential names are expected to be defined explicitly:

      - ``enable`` : This credential defines the password to be sent when
        bringing routing devices to their enable mode.

      - ``sudo`` : The fsos/ftd plugin expects this credential to contain
        the sudo password.

      - ``ssh`` : When setting up an sshtunnel against a server specified in
        a pyATS testbed servers block, this credential must be defined against
        that server block.

    - The ``login_creds`` argument (specified either in pyATS connection
      block or as a `unicon.Unicon.Connection` parameter), now controls
      the order credentials are applied when username/password prompts are
      received while connecting to the device.

    - The ``prompts/login`` and ``prompts/password`` parameters are now
      expected to be explicitly set in the pyATS connection block or
      as `unicon.Unicon.Connection` parameters.

    - The switchover service now accepts a ``switchover_creds`` parameter that
      allows users to define what credentials to use should a username or
      password prompt occur during switchover.

    - The reload service now accepts a ``reload_creds`` parameter that
      allows users to define what credentials to use should a username or
      password prompt occur during reload.

  - The execute service no longer responds to username/password requests,
    users are expected to pass in their own dialog if this kind of handling
    is required.


- generic plugin

  - add flatten_splitlines_command method in generic utils to flatten commands

  - add get_handle method in BaseService for all services to reuse

  - add bulk argument for Configure service to send commands in one sendline

  - refactor generic Configure service, and now HaConfigureService inherits from Configure

  - fix several bugs in BaseService and generic HaExecService


- iosxr plugin

  - fix potential bugs in iosxr execute and configure related services

  - add HaAdminExecute and HaAdminConfigure services for iosxr

  - fix asr9k plugin services admin_execute, admin_configure and admin_bash_console on 64-bit asr9k

  - added dual RP support to iosxr/spitfire plugin.


- junos plugin

  - fix junos plugin configure service


- nxos plugin

  - added VDC related robot commands.


- asa plugin

  - added warning to ASA plugin patterns.


- ios plugin

  - added vrf support in ios plugin ping service. It now accepts vrf as input and passes it as part of the ping command
