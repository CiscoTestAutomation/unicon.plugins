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


