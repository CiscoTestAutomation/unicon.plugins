December 2019
=============

December 17th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.12


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

  - enhance Connection logfile to handle special characters in hostname and alias

- generic plugin

  - add "Invalid host" error pattern for ping service

  - enhance copy service to handle wildcard copy

- asa plugin

  - asa plugin is now using hostname in prompt patterns

- aireos plugin

  - handle 'Press Enter to continue' prompt following certain command

  - enhance command error pattern which has % character before Error
