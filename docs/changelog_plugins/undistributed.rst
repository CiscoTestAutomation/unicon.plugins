--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* iosxr
    * Fixed learn_hostname not working for iosxrv9k platform

* generic
    * Fix the default dialog statements used in reload services
    * Fix reload service to return True or False instead of raise an exception

* nxos
    * configure will raise incomplete command error when appropriate

* iosxr/spitfire
    * Use generic pre-connection statement list to handle syslog messages on connect

* linux
    * Add `sudo` service


