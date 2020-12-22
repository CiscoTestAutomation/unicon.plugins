Feb 2017
========

Feb 8 - v2.2.1
--------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.2.1


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^
  - New core feature - hostname learning:

    - Allows the already configured device hostname to be learned if it
      is not known.

    - Multiple plugin updates to ensure compatibility with this feature
      (generic, iosxv, iosxr, nxosv).

  - Plugin updates:
    - Cheetah AP support

    - Generic plugin updates:

      - Updated rommon pattern to better match several IOS and IOSXE devices.

      - Now stringifying service commands to allow them to be passed as
        non-string objects.

      - Now allowing for list-like and string-like input objects.

      - telnet escape character callback now waits for a limited time
        for chatter to cease before calling sendline.

    - nxos plugin updates:

      - Now allowing for list-like and string-like input objects.

    - iosxe/csr1000v plugin updates - tuned timing parameters

    - iosxr plugin updates:

      - Tuned timing parameters for iosxrv

      - Removed partially implemented iosxr HA execute service, now
        using generic plugin implementation.

  - Core updates:

    - Support for ``%N`` hostname substitution outside statemachine.
      Needed by some uniclean plugins.

    - Now stringifying objects before sending via spawn.

    - pyATS adapter updates:

      - Now properly rendering start when port specified.

      - Now assigning series and model correctly.

      - Now stringifying the IP address in case it is passed in as an object.
