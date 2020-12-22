July 2018
=========


Jul 16 - v3.2.0
---------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v3.2.0


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

.. warning::

    Please be advised that some changes have been introduced into the execute
    service that may be potentially backwards incompatible for some users.

    - The execute service no longer forces enable mode as its start and end
      state.

    - The execute service now returns a dictionary when multiple commands
      are passed either in a list or via a multiline string.

    - Multiline strings are now executed line by line, expecting a prompt after
      each line. This may not address all scenarios, users may need to change
      their command to use a list with multiline string as documented in the
      user guide.

- New plugin: StarOS with support for Starent OS.

- New plugin: Firepower Extensible Operating System (FXOS).

- Robot keyword fixes:

    - Correctly use configure timeout.

    - Fix send control character.

- ConfD plugin update:
  Added option to ignore chatty terminal output with execute() and configure()
  services.


- Generic plugin updates:

  - Updated generic yes/no pattern.

  - Limit the number of password attempts by the default password handler to 3.

  - Fix default password handler logic that alternates between
    enable and tacacs password.


- Add bash_console service for IOSXE and NXOS, add attach_console for NXOS.


- Enhanced NXOS/IOSXE/IOSXR plugins to accomodate pyATS :ref:`connectionpool`
  feature.


- Core feature updates:

  - Added SSH tunnel feature

  - Changed backend buffer matching to use maximum search buffer size
    (default: 8K bytes).  This change significantly improves pattern matching
    speeds for large command output.

  - Bug fix for line_password that was passed incorrectly.

  - CLI proxy bugfix for ssh username not being specified.

  - Refactored service error pattern handling to match by line.


- Mock device updates:

  - Added SSH server support.

  - Support for device hostname variable %N.

  - Fix usage of mock device directory parameter.


- IOSXR admin pattern updates:

  - Added ASR9K series handles for admin patterns.

  - Updated IOSXRV series admin patterns.
  