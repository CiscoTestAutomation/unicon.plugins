June 2020
============

July 7th
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v20.6


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
* Enhanced device connectivity verification functionality

* Fixed bug in switch to vdc keywords

* Removed old expect_log, use device.log.setLevel to enable/disable debug internal log

* Updates to mock_device to handle keystrokes

* Used %1B for Escape code instead of ESC in mock data
