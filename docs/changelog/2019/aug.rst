August 2019
===========

August 27th
-----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.8


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
- core

  - fix base Connection to log plugin model info

  - fixed XR-UT topology adapter

  - Allow login_creds to be specified in pyATS connect() call to override
    the credentials in the testbed YAML.

- generic plugin

  - add bulk_chunk_lines and bulk_chunk_sleep arguments for generic configure service

  - add generic confirm_prompt_y_n_stmt statement

  - fix copy service issue where retry sometimes exits unexpectedly

  - enhance copy service to send ctrl+c when TimeoutError happens in order to recover device into enable state

- iosxe plugin

  - fix iosxe/csr1000v plugin services

  - add iosxe/cat3k/ewlc plugin

  - add iosxe/csr1000v/vewlc plugin

- aireos plugin

  - add prompt_recovery support for aireos reload service

- linux plugin

  - Update the Linux and ise plugins to properly detect a failed password attempt.

- ios plugin

  - add error_patterns verification for ios execute service


August 7th
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.7.5


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Change to the following plugins iosxr, iosxr/spitfire, generic, nxos

  - When prompting for administrator's password, the current credential is
    now reused.

August 2nd
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.7.4


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Introduction of nxos/n5k plugin

- Spawn now sets terminal size on a best-effort basis.

- Fixed issue preventing many services from being called in a multithreaded
  environment.

August 1st
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.7.3


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Fixed iosxr plugin issue that was preventing the standby RP from being
  detected.


