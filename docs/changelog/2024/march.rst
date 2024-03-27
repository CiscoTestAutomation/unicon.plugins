March 2024
==========

 - Unicon v24.3 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.3 
        ``unicon``, v24.3 

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
                                      New                                       
--------------------------------------------------------------------------------

* backend
    * Option to use `UNICON_BACKEND` environment variable to select backend


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* bases
    * connection
        * add operating_mode to the connection object


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* discovery_tokens
    * Add prompt_recovery to dialog

* iosxe
    * Connection provider
        * Add support for operating mode detection on connect()


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxr
    * Modified connection provider
        * Updated connection provider for handeling token discovery.


