November 2019
=============

November 26th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.11



Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
- core

  - separate plugins from unicon to be a sinlge package unicon.plugins

  - use mock_device_cli instead of python run mock_device

  - add matched_retries for Statement to avoid transient match on output

  - enhance UniconStreamHandler to handle UnicodeEncodeError

  - enhance RawPtySpawn to set environment variable via via settings

  - enhance RawSpawn to use shlex for start command split

  - now allow settings.DEFAULT_LEARNED_HOSTNAME to be used by plugins

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
