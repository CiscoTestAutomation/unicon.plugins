August 2020
============

August 25th
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v20.8


Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
* Infrastructure changed to support multi-connections(dual, stack & quad)
* Infrastructure changed to support learn os feature in generic plugin
* Enhanced cli proxy feature, now can support HA device
* Allowed to set the connection terminal size via ROWS and COLUMNS environment variables for the connection
* Updated spawn read method to ignore non-utf8 decoder errors
* Allowed prompt_recovery to pass from connection class variable to service variable
* Added trim line option in the unicon logging to trim empty lines
