November 2022
==========

November 28 - Unicon.Plugins v22.11
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.11
        ``unicon``, v22.11

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

--------------------------------------------------------------------------------
                                      Add                                       
--------------------------------------------------------------------------------

* generic
    * Added support for trex console in linux

* iosxe/sdwan
    * Added config transaction support for ha devices.

* generic
    * configure
        * add allow_state_change for configure service.

--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* sros
    * Updated plugin for error detection and improved configuration handling

* generic
    * Fix the copy service pattern for tftp_addr

* iosxr
    * Modified reload service for asr9k and ncs5k
        * Checking the buffer for settling down and using the connection provider

* topology
    * Modified terminal_server schema doc to capture issues with incorrect schema.