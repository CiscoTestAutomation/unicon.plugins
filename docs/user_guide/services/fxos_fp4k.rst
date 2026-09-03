FXOS/FP4K
=========

This section lists the services which are supported with Firepower Extensible Operating System (FXOS) Unicon plugin
for Firepower 4000 series platforms. This plugin is used when `os=fxos` and `platform=fp4k` are specified.

This plugin is based on the FXOS plugin, for other supported services, see `FXOS <fxos.html>`__

  * `switchto <#switchto>`__

Note: `reload` service has not been implemented at this time.


switchto
--------

The `switchto` service is a helper method to switch between CLI states. This can be used to switch
to more specific states than e.g. the ``fxos`` method.

The following states are supported:

 * `enable`
 * `disable`
 * `config`
 * `ftd`
 * `expert`
 * `sudo`
 * `fxos`
 * `fxos scope \<path\>`
 * `fxos mgmt`
 * `adapter [<id>]`
 * `cimc [<id>]`
 * `module [<id>] [console|telnet]`
 * `fxos switch`
 * `adapter shell`
 * `adapter shell fls`
 * `adapter shell mcp`

===================   ========================    ====================================================
Argument              Type                        Description
===================   ========================    ====================================================
to_state              str or list                 target state(s) to switch to
timeout               int (default 60 sec)        timeout value for the command execution takes.
===================   ========================    ====================================================

