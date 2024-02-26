February 2024
==========

February 27 - Unicon.Plugins v24.2 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.2 
        ``unicon``, v24.2 

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

* generic
    * Add EOF statement to handle connection loss when using telnet backend

* iosxe
    * Added below config error patterns
        * % Invalid address
        * % Deletion of RD in progress; wait for it to complete


--------------------------------------------------------------------------------
                                      Add                                       
--------------------------------------------------------------------------------

* utils
    * Update assertRegexpMatches to assertRegex to fix attribute error in python 3.12


