May 2021
========

May 25
------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.5
        ``unicon``, v21.5

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
                                      New                                       
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* dialog processor
    * Modified the prompt_recovery logging message so it's more clear.
    * Modified dialog processer logic to avoid duplicate match data when trim_buffer is False

* connection
    * Updated connection class 'connected' logic to detect connection closure by remote device
    * Modified connect() implementation to return the complete connection log

* sshutils
    * Use netstat command to find available port for ssh tunnel
