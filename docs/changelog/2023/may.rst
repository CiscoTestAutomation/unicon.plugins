May 2023
==========

May 30 - Unicon v23.5 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v23.5 
        ``unicon``, v23.5 

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

* backend
    * Pass device object to Spawn class

* unicon.bases.routers.connection_provider
    * Modified logic in designate_handles to use plugin settings

* bases
    * Modified Connection
        * Expanded PauseOnPhrase to be able to pause on device output


