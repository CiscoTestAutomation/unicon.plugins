April 2019
==========

April 29th
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.4.0


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- learn_hostname feature updated to allow common plugin-specific default device
  names such as `Router` to be learned if no hostname has been set on the
  device.

- The iosxr plugin enable pattern is now more strict.

- Removal of legacy proxy implementation

- Add timing support for preface in mock_device

- Fix linux statemachine issue on slow connection setup

- Now allowing settings to be replaced when specified as an object on
  connection setup.
  Specifying settings as a dictionary still updates the existing settings.

- New Traceroute command

- Added error patterns to iosxe, iosxr, nxos and fxos plugins.


April 1st
---------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.0.2


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- junos plugin connection statemenent fixes

- Added response for 'Connected.' message on connect (e.g. when connecting via serial console)

- Updated IOSXR enable prompt pattern to fix hostname learning
