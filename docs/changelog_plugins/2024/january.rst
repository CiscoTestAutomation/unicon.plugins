January 2024
==========

30 - Unicon.Plugins v24.1 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v24.1 
        ``unicon``, v24.1 

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

* generic
    * Added more prompt support in connection statement list


--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxe
    * Added unittests to test hostnames with special characters\
    * Update settings for reload API, change SYSLOG_WAIT to 10 seconds
    * cat9k
        * Update image_to_boot for HA device. (active and standby rp)

* generic, iosxe
    * Update config transition logic, increase wait time for prompt

* generic
    * Update response to setup dialog to "no" instead of "n"

* linux
    * Update linux hostname learning pattern to handle ANSI characters in prompt


