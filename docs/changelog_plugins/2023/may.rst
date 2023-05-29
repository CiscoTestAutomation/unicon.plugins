May 2023
==========

May 30 - Unicon.Plugins v23.5 
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

* generic
    * If 'connection refused' is seen on connect, try to clear the console line
    * Update reload pattern to support quick reload prompt

* iosxe
    * Update tclsh pattern to handle truncated hostnames

* junos
    * Update prompt patterns to avoid backtracking

* iosxr
    * Fix start command for moonshine HA connections


--------------------------------------------------------------------------------
                                     Modify                                     
--------------------------------------------------------------------------------

* iosxr
    * asr9k
        * Modified call_service in service_implementation
            * removed genie dependency


