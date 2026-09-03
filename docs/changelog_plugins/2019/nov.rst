November 2019
=============

November 27th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v19.11.1


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

- aireos plugin

  - remove f-strings that is not supported on python 3.4 and 3.5


November 26th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v19.11


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

- generic plugin

  - add prompt matched_retries for execute service to avoid transient match on output

  - add resolve_as_number option for traceroute service

- nxos plugin

  - add corresponding error patterns for configure service

- linux plugin

  - enhance linux plugin to set TERM vt100 and LC_ALL C by default

- iosxe plugin

  - enhance iosxe/cat3k to find boot image from rommon

  - add vrf argument for iosxe traceroute service

- sdwan plugin

  - add plugins sdwan/viptela and sdwan/iosxe

- aireos plugin

  - enhance to support known states

  - enhance to support for hostname learning

  - now execute service raises SubCommandFailure if error is detected in CLI output.
