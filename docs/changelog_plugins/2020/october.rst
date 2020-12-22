October 2020
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v20.10


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

* [Generic] Fix switchover service issue while trying to bring standby rp to enable mode

* [IOSXE] Enhance stack switchover service to handle username/password prompt
* [IOSXE] Enhancing IOSXE configure service for supporting wireless controllers different prompts

* [NXOS] Added plugin specific configure service allowing commit functionality

* [Linux] Added regex pattern for handling ESXi server prompt

* [JUNOS] Changed self.commit_cmd from 'commit' to 'commit synchronize'
* [JUNOS] Added regex pattern to self.CONFIGURE_ERROR_PATTERN
