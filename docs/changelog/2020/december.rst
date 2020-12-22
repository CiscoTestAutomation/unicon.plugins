December 2020
=============

December 15th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v20.12


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

* Added feature to extend list settings from testbed file
* Fixed log issue when pyats managed_handlers's tasklog stream is None
* Fixed parse_spawn_command for ha device to get the right subconnection context
* Fixed ssh command username issue
* Enhacnced ha device connectivity check
