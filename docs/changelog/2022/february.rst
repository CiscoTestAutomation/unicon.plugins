February 2022
==========

February 24 - Unicon v22.2 
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.2 
        ``unicon``, v22.2 

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

* routers/connection provider
    * Updates to allow hostname learning when device is found in config mode

* bases
    * Modified BaseCommonRpConnectionProvider
        * Added shared implementation of learn_tokens method to reduce duplicate code
    * Modified BaseSingleRpConnectionProvider
        * Remove duplicate code from learn_tokens
    * Modified BaseMultiRpConnectionProvider
        * Remove duplicate code from learn_tokens


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* statemachine
    * add_path
        * add index to identify where to add the new path in self.paths
    * add_state
        * add index to identify where to add the new state in self.states


