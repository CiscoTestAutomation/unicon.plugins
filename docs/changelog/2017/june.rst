June 2017
=========

June 28 - v2.3.1
----------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.3.1


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

The following changes were introduced:

- Introduction of new plugins : asa and nso

- Added generic device mocking infrastructure to enable plugin unit test.

- pyATS testbed/topology support

  - Added support for 'port' option in pyATS testbed file with SSH protocol.
    You can now specify the port in the testbed file when SSH is used,
    the port will be added as '-p <port>'.

- ise plugin

    - Bug fix (LINUX_INIT_EXEC_COMMANDS not found)
    - Refactored prompt to include hostname

- linux plugin

    - Corrected prompt pattern

- nxos plugin

    - Fixes to IPv6 ping

    - Now using "show system redundancy status" instead of "sh redundancy status"
