April 2021
==========

April 27th
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.4
        ``unicon``, v21.4

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
* adapters.topology
    * Modified Unicon:
      * Fixed - debug argument not being propagated in multi_rp connections

* Dialog processor
    * Modified SimpleDialogProcessor:
      * log statement debugs via debug log level
      * Removed STATEMENT_LOG_DEBUG settings, use connect(debug=True) instead
* NXOS service statments
    * Added new statment to handle multiple call for abort provisiong
    * Added new pattern to nxos reload patterns

        
