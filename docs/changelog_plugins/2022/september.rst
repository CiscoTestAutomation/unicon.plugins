September 2022
==========

September 27 - Unicon.Plugins v22.9
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.9
        ``unicon``, v22.9

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
                                      Fix
--------------------------------------------------------------------------------

* generic
    * Added setting for state change prompt retries, default to 3 second wait
    * Update sudo regex pattern
    * Updated the session data to handle the reoccurring dialog issue
    * Update copy error pattern to ignore self-signed certificate failure
    * Add handlers for ping options extended_verbose, timestamp_count, record_hops, src_route_type

* iosxr/ncs5k
    * Updated the mock data for ncs5k

* iosxe
    * Added a RELOAD_WAIT to iosxe settings

* hvrp
    * Updated the pattern and setting to support configuration and error detection.


