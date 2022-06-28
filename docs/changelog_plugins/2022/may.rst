May 2022
==========

May 31 - Unicon.Plugins v22.5 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.5 
        ``unicon``, v22.5 

Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon.plugins
    bash$ pip install unicon

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon.plugins
    bash$ pip install --upgrade unicon

Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe
    * Updated prompt stripping util for configure service
    * Add macro state to statemachine and configure service

* iosxe/cat9k
    * Added reload service for HA connections

* mock data
    * updated mock data, replaced hostname with %N

* ios/pagent
    * Add state for emulator prompt

* generic
    * Update PID mapping file, rename some of the tokens. Use lowercase for model.

* iosxr
    * Update bash prompt pattern


