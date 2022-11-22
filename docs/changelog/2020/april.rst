April 2020
============

April 28th
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v20.4


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
* Fixed unittests failures seen with multiprocessing on Mac-py38 environment

* Added `goto_enable` and `standby_goto_enable` key to generic connect service to
  allow user to disable device behavior of going to enable state in every device
  connect call, Default is True not to interrupt intuitive device behavior

* Added dialog callback for credentials

* See also the unicon.plugins changelog.

