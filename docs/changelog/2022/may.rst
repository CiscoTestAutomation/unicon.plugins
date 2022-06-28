May 2022
==========

May 31 - Unicon v22.5 
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

* router connection provider
    * Updated hostname learning for HA connections

* mock device
    * Added ctrl-c handler while writing output


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* enhancement for retry and service_dialog arguments
    * Allow user to simply pass empty list to initialize with empty dialog


