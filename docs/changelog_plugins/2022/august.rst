August 2022
==========

August 30 - Unicon.Plugins v22.8
------------------------



.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon.plugins``, v22.8
        ``unicon``, v22.8

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

--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* generic
    * Update the default hostname pattern to avoid matching enable pattern against config prompt
    * Update syslog regex pattern for guestshell log message

* iosxe
    * Added new config prompts related to getvpn gdoi in patterns.py
    * Added wsma prompts to config prompt pattern
    * Refactor grub boot handler
    * Refactor iosxe reload service, rename context variable boot_image to grub_boot_image
    * Update press_any_key regex pattern
    * Update grub_prompt regex pattern
    * Add escape char regex setting `ESCAPE_CHAR_PROMPT_PATTERN`
    * Add grub regex pattern setting `GRUB_REGEX_PATTERN` to match menu entries

* linux
    * Updated linux prompt pattern

* general
    * Update regex patterns in CopyPatterns to be more strict

* iosxe/cat9k
    * Updated the container shell prompt pattern

* iosxe/cat8k
    * Added Reload and HAReload

