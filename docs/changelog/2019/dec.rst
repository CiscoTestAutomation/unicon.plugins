December 2019
=============

December 19th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v19.12.1


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

- Introduction of ios/pagent plugin


December 17th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v19.12


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

  - add "Invalid host" error pattern for ping service

  - enhance copy service to handle wildcard copy

- asa plugin

  - asa plugin is now using hostname in prompt patterns

- aireos plugin

  - handle 'Press Enter to continue' prompt following certain command

  - enhance command error pattern which has % character before Error
