July 2020
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v20.7


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

* Fixed unittest corresponding to check connectivity enhancement

* Reverted back commit_retry until getting confirmation from the user

* [LINUX] Updated truncate_trailing_prompt to accept regex without regex groups

* [IOSXE] Fixed IOSXE state machine enable to disable dialog issue

* [IOSXR] Added configure_exclusive service to IOSXR plugin

* [NXOS] Enhanced NXOS reload service added reconnect_sleep argument
* [NXOS] Fixed incorrect login when password prompt occur before the username prompt

* [APIC] Enhanced apic configure prompt pattern to support various configure prompt
