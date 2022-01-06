August 2021
========

August 31st
------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.8
        ``unicon``, v21.8

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
    * Refactored ping service
        * Automatically set extd_ping to 'y' if extended option is specified
        * Handle invalid input errors
        * Add address to ping command if no other options are given
        * Deprecated arguments `int` and `src_addr` for ``interface`` and ``source``
    * Modified reload service, added `raise_on_error` option


