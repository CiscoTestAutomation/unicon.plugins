May 2018
========


May 12 - v3.1.2
---------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v3.1.2


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
- IOSXE plugin updates:

  - Fixed a minor bug in the newly refactored ping service, now an explicitly set
    ping command has the highest precedence.



May 7 - v3.1.1
--------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v3.1.1


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
- IOSXE plugin updates:

  - Refactored the ping service to allow it to properly handle vrf
    specification.

- NXOS plugin update:

  - now bash_console() ``feature bash`` command respects timeout value
