January 2020
=============

January 28th
-------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v20.1


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

- Introduction of sros plugin for Nokia SR devices.

- Added switchto service to iosxr/spitfire plugin.

- aireos plugin:

  - Handle 'Would you like to save them now?' prompt.

- nxos and fxos/ftd plugins:

  - Fix a bug where credentials were not properly converted to plaintext.

- iosxe plugin

    - Now copy service passes in vrf via the command line instead of
      expecting to be prompted for vrf.

    - iosxe configure service now responds to confirm/want to continue prompts.

- generic and iosxe/cat3k plugins

    - Fixed reload service timeout issue, now waiting longer when
      connecting after reload.
