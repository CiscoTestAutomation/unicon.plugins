August 2017
===========

August 10 - v2.3.4
------------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.3.4


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

The following changes were introduced:

- generic plugin

    - Refactored telnet handler to allow plugin-specific delay after
      initial telnet to the device and before pressing <Enter>.

- iosxe/csr1000v plugin

    - Added initial telnet delay before pressing <Enter> to prevent
      timeouts when connecting to some image variants.

August 8 - v2.3.3
-----------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.3.3


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

The following changes were introduced:

- Linux plugin

    - Refactored prompt stripping for the execute service. 

- Generic plugin

    - Refactored copy service to be more real-time efficient.

- Device mocking

    - Added mock devices for various iosxe flavors : asr, isr, cat3k.

    - Other packages may now invoke mock devices from their unit tests.
