December 2017
=============

December 20 - v2.3.8
--------------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.3.8


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Updates to Linux plugin:

  - Added 'hit and enter' prompt

  - Prompt pattern speed fix

  - Added unittest for pattern speed


- Updates to ConfD plugin:

  - Support for CSP (Cloud Services Platform)


- Updates to iosxr plugin:

  - Pattern updated to capture the device output in addition to device prompt


- Updates to iosxr/moonshine plugin:

  - Improved support for confirmation prompt y/n handling


- Updates to iosxe/cat3k and nxos plugins:

  - Fixed some cases in which prompt recovery was not being properly invoked.

- Updates to iosxe and nxos plugins:

  - Fixed a day-one bug, now post-reload HA sync detection loop works correctly.

- Generic patterns

  - Updated bad_password pattern


- IOS unittest update

  - Added test for password error handling


- Mock device updates:

  - Get response text from a list of responses (linear or circular)

  - Mock data loading from directory specified on cli


- Developer updates:

  - Support for callable as statemachine command

  - Dotgraph method to create graphical representation of the statemachine
