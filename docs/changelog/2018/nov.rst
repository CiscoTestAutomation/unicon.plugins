November 2018
=============

Nov 27 - v3.4.3
---------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

    ``unicon``, v3.4.3


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^

- Raise EOF exception if spawn closed or terminated.

- Add new ``junos`` plugin to support Juniper devices.

- Reload service:

    - Send 'n' key only once for POAP prompt.

- Add new services to the ``iosxr`` plugin:
     - attach_console
     - bash_console
     - admin_console
     - admin_attach_console
     - admin_bash_console


Nov 15 - v3.4.2
---------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

    ``unicon``, v3.4.2


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^

- Copy Service

    - Added reply parameter for passing additional Dialog.

    - Server parameter is no longer mandatory if source or dest contains
      the server IP address.

    - The dest_file parameter may now be specified on nxos platforms.


- Configure Service

  - Bug fix to improve support for large configurations by ensuring the
    ``timeout`` parameter is properly respected.


- Reload Service

  - Fixed an issue seen on nxos reload by tightening up the configure
    prompt pattern.


- iosxr Plugin

  - Bug fixes to confirm prompt handling.
