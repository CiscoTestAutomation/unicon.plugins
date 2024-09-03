September 2024
==========

September 24 - Unicon.Plugins v24.8 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.8 
        ``unicon``, v24.8 

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
                                      Add                                       
--------------------------------------------------------------------------------

* pid_tokens
    * add pid entry for ir1800 device


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* generic
    * Update execute() service log message to include device alias
    * Update unittests to handle authentication exceptions
    * Update unittests for token learning

* iosxr
    * Update more prompt handling to support (END) prompt


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxr
    * New `monitor` service for IOS-XR with support for "monitor interface" command.


