April 2018
==========

April 30 - v3.1.0
-----------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v3.1.0


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

    # to use the new robot-framework dependencies, d:
    bash$ pip install unicon[robot]


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
- Updated XR prompt pattern to match complete prompt

- Added back os.sync to send method as this was causing issues on some platforms.

- Updates in generic plugin escape handler
    After connecting to a device via console server, do not send 'enter'
    if an authentication prompt is shown

- added ``unicon.robot`` module: now Unicon comes with robot-framework keywords.

- note that you must install robotframework in order to import ``unicon.robot``
  module.
