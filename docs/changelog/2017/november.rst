November 2017
=============

November 18 - v2.3.7
--------------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.3.7


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- New plugin: Voice Operating System (VOS)

- New plugin: Cisco Integrated Management Console (CIMC)

- Updates to generic plugin:

    - pattern update for [confirm] prompt

    - documentation updates to clarify default Dialog for execute service


- Updates for ConfD plugin

    - prompt pattern matching update

    - NSO plugin now using confd implementation


- Topology handling for linux connection

    - fixed regression with command option for linux connection


- NXOS shellexec documentation update

    - example use of 'sudo'


- Mock device updates

    - raise error on duplicate state in yaml files


- Updates to aireos, confd, generic, ise, nxos plugins

    - Updated plugin regex patterns to improve speed
