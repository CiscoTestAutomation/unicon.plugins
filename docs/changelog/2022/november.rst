November 2022
==========

November 28 - Unicon v22.11
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.11
        ``unicon``, v22.11

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

* Router
    * Removed timeout_pattern in BaseServices:
        The timeout pattern was causing issues as it was getting matched for device output instead actual error pattern.
* Connection
    * Modified logic for pattern detection of existing username
        Previous pattern detection for username would match if username was used in the ProxyJump ssh option.