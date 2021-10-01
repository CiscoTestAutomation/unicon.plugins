--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* generic
    * Fixed reload dialog for HA connections to handle enable secret prompts
    * Fix syslog handler timeout to avoid endless dialog
    * Update syslog handler to only send return one time when a syslog message is seen
    * Fix standby state detection in switchover() service
    * Fix the default dialog statements used in reload services
    * Fix reload service to return True or False instead of raise an exception
    * Add syslog handler to reload statement list
    * Updated syslog message regex for 'syslog_wait_send_return'

* iosxe
    * Added documentation for rommon() service

* nxos
    * configure will raise incomplete command error when appropriate

* iosxr
    * Fixed learn_hostname not working for iosxrv9k platform

* iosxr/spitfire
    * Use generic pre-connection statement list to handle syslog messages on connect

* linux
    * Add `sudo` service


--------------------------------------------------------------------------------
                                      New
--------------------------------------------------------------------------------

* nxos
    * Added `sqlite` state to the statemachine

