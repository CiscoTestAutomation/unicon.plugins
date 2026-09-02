September 2016
==============

September 30
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.1.0b14

Features:
^^^^^^^^^

 - Increased post-prompt wait for iosxrv plugin to better ensure device
   is ready for configuration before configuration is attempted.


September 29
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.1.0b13

Features:
^^^^^^^^^

 - Added trim_buffer=False to expect during iosxrv and iosxrv9k launchup check.


September 28
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.1.0b12


Features:
^^^^^^^^^

 - NXOSv mini-cleaner tuning to account for the virtual platform
   displaying extra console text after the switch# prompt.


September 27
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.1.0b11


Features:
^^^^^^^^^

 - NXOSv mini-cleaner tuning to account for the virtual platform
   displaying extra console text after the login: and Password: prompts.

 - Linux plugin fix for parsergen integration issue.


September 26
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.1.0b10


Features:
^^^^^^^^^

 - Introduced mini-cleaner for iosxe/csr1000v
   (required by dyntopo/laas to launch Ultra virtual devices).

 - Tuned the iosv, iosxrv, nxosv and iosxrv9k plugins
   to behave better when running on a heavily loaded execution server.


September 23
------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v2.1.0b9


Features:
^^^^^^^^^

 - Introduced mini-cleaner for iosxrv
   (required by dyntopo/laas to launch XRVR).
