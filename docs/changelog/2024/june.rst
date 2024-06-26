June 2024
==========

 - Unicon v24.6 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.6 
        ``unicon``, v24.6 

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

* stackswitchover
    * Modified to wait for known switch state before continuing to check all stack members

* stackreload
    * Modified to always check all stack memebers after reload
    * Modified to work for newer platforms

* iosxe/stack
    * Reload Service
        * fix the logic for reloading stack devices to wait for all the members to be ready.


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe.stack.utils
    * Added new method wait_for_any_state
        * wait for any known state to bypass possible timing issues


