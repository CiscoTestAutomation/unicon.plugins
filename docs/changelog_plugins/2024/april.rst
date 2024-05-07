April 2024
==========

 - Unicon.Plugins v24.4 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.4 
        ``unicon``, v24.4 

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
    * Use stricter pattern for enable password
    * Update standby locked pattern
    * Add connection closed statement to execute service
    * Add standby locked state to single RP statemachine
    * Update escape character handler timing settings
    * Revert adding connection closed statement to execute service
    * Update config transition logic
    * Add `result_check_per_command` option to disable/enable error checking per configuration command

* iosxe
    * Fix operating mode logic
    * More prompt handling updated
    * Added statements to token discovery dialog

* iosxr
    * Add standby locked state to single RP statemachine
    * Change default behavior of ``configure()`` service, error check after all commands by default
    * Add handler for `show configuration failed` errors to ``configure()`` service.
    * Add `SHOW_CONFIG_FAILED_CMD` setting for command to use, default `show configuration failed`

* other
    * update pid token list


