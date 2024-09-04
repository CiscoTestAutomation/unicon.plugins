August 2024
==========

August 27 - Unicon v24.8 
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
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon.bases
    * Added message argument to log_service_call

* unicon.statemachine
    * Modified Exception handling, propagate authentication failures

* unicon
    * topology
        * Fixed logic for proxy connection.
    * sshtunnel
        * Added -o EnableEscapeCommandline=yes to ssh-options.

* unicon.eal.backend
    * Modified telnet backend
        * improved option negotiation
        * Added informational RTT log message


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* unicon.adapter
    * Modified topology adapter to support enxr

* unicon.core.errors
    * Add new exception LearnTokenError

* unicon.bases
    * Update exception handling to raise LearnTokenError without closing connection


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* iosxe
    * Modified Rommon service
        * Allowing for a config-register parameter to the rommon service


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* unicon.plugins.generic
    * Modified password_handler
        * Have it check for tacacs_password first


