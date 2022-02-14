December 2021
=============

December 14 - Unicon v21.12
---------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v21.12
        ``unicon``, v21.12

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

* playback
    * Mock
        * Refactored mock to work with Aireos devices

* bases
    * Modified routers services
        * Corrected service log message


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* playback
    * _mock_helper
        * Created helper module to handle various device commands


