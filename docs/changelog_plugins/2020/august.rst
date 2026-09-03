August 2020
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v20.8


Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon.plugins


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon.plugins


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

* Updated terminal size settings for NXOS/ACI/N9K and linux plugins.

* [APIC] Added 'Error' to the list of error_patterns

* [ASA] Added statement to handle for 'Proceed with reload?'

* [IOSXE] Changed IOSXE plugin shell_prompt (non-greedy match on wildcard)
* [IOSXE] Added stack and quad plugins to support devices with stack/quad chassis type

* [IOSXR] Updated IOSXR/ncs5k STANDBY_STATE_REGEX in the setttings
* [IOSXR] Added asr9k/ncs5k ha reload service

* [Generic] Added learn_os feature for generic plugins redirect to corresponding plugin connection
