March 2022
==========

March 29 - Unicon.Plugins v22.3 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.3 
        ``unicon``, v22.3 

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

* iosxe
    * Add support for switch and rp keyword arguments for bash console service
    * Added host-list to config pattern

* iosxe/cat8k
    * Fix switchover service transitions

* all
    * Moved the pid_tokens.csv file to properly include it during packaging

* generic
    * Added broken pipe to the reload connection_closed pattern
    * Fix loading of token info file

* dnos6
    * NON BACKWARDS-COMPATIBLE CHANGE removed dell os and os6 platform, replaced with dnos6 os


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* dnos10
    * added plugin support for dnos10


