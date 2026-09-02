March 2019
==========

March 12th
----------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.0.1


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Fix bug where prompt recovery was not applied on initial connection during
  init command execution.

- Fix bug to ensure protocol is not required in connection block when command
  key is specified.

March 4th
---------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v19.0


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- Introducing the new iosxr/spitfire plugin for Lindt platform.

- Record new doc, and fix a limitation for cython package.

- Add enable password option in utils clear_line

- Support passing of settings object as Settings() class, dict or AttributeDict

- support for python 3.7

- Add support for custom login and password prompts.

- New Robot keyword to set Unicon settings.
