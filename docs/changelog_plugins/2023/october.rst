October 2023
==========

October 31 - Unicon.Plugins v23.10
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v23.10
        ``unicon``, v23.10

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

* generic
    * Empty sendline to get the prompt for go_to any state

* iosxe/cat9k
    * Updated container ssh prompt pattern

* nxos
    * Modified
        * Added alt_cred password lab2 in nxos_mock_data_n5k.yaml


--------------------------------------------------------------------------------
                                      New                                       
--------------------------------------------------------------------------------

* generic
    * Adding fallback credentials for handling authentication failure.

* iosxe
    * Adding new password statement for setting up the password on the device after the device has booted in controller mode.


