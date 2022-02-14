NXOS
====

This section lists down all those services which are only specific to NXOS.
For list of all the other service please refer this:
:doc:`Common Services  <generic_services>`.

.. important::

    In argument table

    * values in parenthesis are default values.
    * mandatory arguments are marked with `*`.


shellexec
---------

Service to execute commands on the Bourne-Again SHell (Bash).


==========   ======================    ========================================
Argument     Type                      Description
==========   ======================    ========================================
timeout      int (default 60 sec)      timeout in sec for executing command on shell.
reply        Dialog                    additional dialog
command      list                      List of command to execute on shell
target       standby/active            by default commands will be executed on active,
                                       use target=standby to execute command on standby.
==========   ======================    ========================================


.. code-block:: python

    rtr.shellexec(['uname -a'])

    cmd = ['uname -a', 'ls -l']
    rtr.shellexec(cmd)


If you want to run bash commands as root in the Linux shell, you can add `sudo su root`
to the command list. Please note that you need to add 'exit' explicitly to the command
list to return to the user bash shell. (The `shellexec` service will automatically
execute another 'exit' command to return to the NXOS command prompt.)

.. code-block:: python

    cmd = ['sudo su root', 'uname -a', 'whoami', 'exit']
    rtr.shellexec(cmd)


Note: if the sudo prompt asks for a password, you need to pass the `reply` Dialog object
to respond to the password prompt.  Credentials are available in ``rtr.credentials``.

.. code-block:: python

    from unicon.eal.dialogs import Dialog
    from unicon.plugins.generic.statements import GenericStatements
    statements = GenericStatements()
    password_stmt = statements.password_stmt

    cmd = ['sudo su root', 'uname -a', 'whoami', 'exit']
    device.shellexec(cmd, reply=Dialog([password_stmt]))


configure
---------

Service to execute commands on configuration mode.

================  ========================    ====================================================
Argument          Type                        Description
================  ========================    ====================================================
command           list                        list of commands to configure
reply             Dialog                      additional dialog
timeout           int                         timeout value for the command execution takes.
error_pattern     list                        List of regex strings to check output for errors.
prompt_recovery   bool (default False)        Enable/Disable prompt recovery feature
target            str (default "active")      Target RP where to execute service, for DualRp only
mode              str (default: "default")    Mode to configure ("default" or "dual")
================  ========================    ====================================================


.. code-block:: python

    rtr.configure(['feature isis', 'commit'], mode="dual")

    # config dual-stage
    # Enter configuration commands, one per line. End with CNTL/Z.
    # R1(config-dual-stage)# feature isis
    # R1(config-dual-stage)# commit
    # Verification Succeeded.

    # Proceeding to apply configuration. This might take a while depending on amount of configuration in buffer.
    # Please avoid other configuration changes during this time.
    # Configuration committed by user 'admin' using Commit ID : 1000000002
    # R1(config-dual-stage)# end
    # R1#


If you want to bring device to configure dual stage, you can use the `go_to` function in state machine
and use `'config_dual': True` as the context. The following is an example to do that.

.. code-block:: python

    rtr.state_machine.go_to('config', rtr.spawn, context={'config_dual': True})

    # config dual-stage
    # Enter configuration commands, one per line. End with CNTL/Z.
    # R1(config-dual-stage)#

    # execute command in configure dual stage
    rtr.execute('no logging console')

    # R1(config-dual-stage)# no logging console
    # R1(config-dual-stage)# 


attach
------

Service to attach to line card to execute commands in. Returns a
router-like object to execute commands on using python context managers.

====================    ======================    =================================================
Argument                Type                      Description
====================    ======================    =================================================
module_num              int                       module number to attach to
timeout                 int (default 60 sec)      timeout in sec for executing commands
target                  standby/active            by default commands will be executed on active,
                                                  use target=standby to execute command on standby.
====================    ======================    =================================================

.. code-block:: python

    with device.attach(1) as lc_1:
        output1 = lc_1.execute('show interface')


attach_console
--------------

Service to attach to line card console to execute commands in. Returns a
router-like object to execute commands on using python context managers.

====================    ======================    ========================================
Argument                Type                      Description
====================    ======================    ========================================
module_num              int                       module number to attach console to
login_name              str                       name to login with, default: root
default_escape_chars    str                       default escape char, default: ~,
change_prompt           str                       new prompt to change to for ez automation
timeout                 int (default 60 sec)      timeout in sec for executing commands
prompt                  str                       bash prompt (default: bash-\d.\d# )
====================    ======================    ========================================

.. code-block:: python

    with device.attach_console(1) as lc_1:
        output1 = lc_1.execute('ls')
        output2 = lc_1.execute('pwd')

ping6
-----

Service to issue ping6 response request to another network from device.

=====================       ===============================================================
Argument                    Description
=====================       ===============================================================
addr                        Destination address
proto                       protocol(ip/ipv6)
count                       Number of pings to transmit
source                      Source address or interface
data_pat                    data pattern that would be used to perform ping.
dest_end                    ending network 127 address
dest_start                  beginning network 127 address
df_bit                      (y/n) y sets the DF bit in the IP header.
dscp                        field DSCP in the IPv6 header.
vrf                         vrf interface name
mask                        Number of bits in the network mask of the target address.
exp                         Experimental (EXP) bits bits in MPLS header
pad                         Pad pattern for MPLS echo request
transport                   destination type as an MPLS traffic engineering (TE) tunnel
oif                         output interface
reply_mode                  reply mode for the echo request packet
size                        ping packet size to transmit
ttl                         time-to-live (TTL) value
tunnel                      Tunnel interface number
tos                         TOS field value
multicast                   multicast addr
udp                         (y/n) enable/disable UDP transmission for ipv6.
interface                   Interface
vcid                        VC Identifier
topo                        topology nam
verbose                     (y/n) enable/disable verbose mode
extended_verbose            Enables extended verbose mode
src_route_type              source type strict/loose
src_route_addr              source route ip
validate_reply_data         (y/n) validate reply data or not
force_exp_null_label        (y/n) Force explicit null label.
lsp_ping_trace_rev          LSP ping/trace revision
precedence                  precedence in the IPv6 header
novell_type                 (y/n) To use the Novell Standard Echo type instead of the Cisco ping echo type.
sweep_ping                  sweep ping command
sweep_interval              sweep interval
sweep_min                   min packet size
sweep_max                   max packet size
extd_ping                   (y/n) enable/disable extended ping.
ipv6_ext_headers            (y/n) include extension header or not
ipv6_hbh_headers            (y/n) include hop by hop option or not.
ipv6_dst_headers            (y/n) include destination option or not.
timestamp_count             number of timestamps
record_hops                 Number of hops
=====================       ===============================================================


    return :
        * ping command response on Success

        * raise SubCommandFailure on failure.

.. code-block:: python

        #Example
        --------

        output = ping6(addr="2001:cdba:0:0:0:0:3257:9652")
        output = ping6(addr="2001:cdba:0:0:0:0:3257:9652", extd_ping='yes')


list_vdc
--------

As the name suggests, it returns the names of all the VDCs in the list format.
Please note that unlike most of the services, the return here is not of type
`str` but `list`.

==========   ======================    =============================
Argument     Type                      Description
==========   ======================    =============================
timeout      int (10)                  timeout value for the overall interaction.
dialog       Dialog                    additional dialog
command      str (switchback)          alternate command.
==========   ======================    =============================

::

    In [6]: vdcs = con.list_vdc()
    2016-04-04T02:40:35: %UNICON-INFO: +++ None  +++
    2016-04-04T02:40:35: %UNICON-INFO: +++ execute  +++
    2016-04-04T02:40:35: %UNICON-INFO: +++ exec show vdc +++
    show vdc

    Switchwide mode is f2e f3

    vdc_id  vdc_name                          state               mac                 type        lc
    ------  --------                          -----               ----------          ---------   ------
    1       step-n7k-2                        active              8c:60:4f:75:53:41   Admin       None
    2       vdc1                              active              8c:60:4f:75:53:42   Ethernet    f2e f3
    3       vdc2                              active              8c:60:4f:75:53:43   Ethernet    f2e f3
    4       vdc3                              active              8c:60:4f:75:53:44   Ethernet    f2e f3
    6       vdc5                              active              8c:60:4f:75:53:46   Ethernet    f2e f3

    step-n7k-2#
    In [7]: vdcs
    Out[7]: ['step-n7k-2', 'vdc1', 'vdc2', 'vdc3', 'vdc5']

.. note::

    You can call this service even when you are in a VDC. It will `switchback`,
    perform the operation and again come back to the same VDC from where you
    executed this API.

switchto
--------

`switchto` is used to switch to any given VDC. This service performs some
basic checks like checking whether the target vdc exists etc. It also makes
sure all the interactions are handled while switching to a VDC for the first
time after creation.

*values in parenthesis represent the default value*

==========   ========================    =============================
Argument     Type                        Description
==========   ========================    =============================
vdc_name*    string                      name of the VDC to switch to
vdc_cred     str ('default')             Credential to use for first time switching.
timeout      int (20)                    timeout value for the overall interaction.
dialog       Dialog                      additional dialog
command      str (switchto vdc)          alternate command.
==========   ========================    =============================

Most of the time simply providing the VDC name is just good enough.

::

    In [3]: con.switchto('vdc1')
    2016-04-04T02:19:28: %UNICON-INFO: +++ switchto vdc  +++
    2016-04-04T02:19:28: %UNICON-INFO: +++ None  +++
    2016-04-04T02:19:28: %UNICON-INFO: +++ execute  +++
    2016-04-04T02:19:28: %UNICON-INFO: +++ exec show vdc +++
    show vdc
    Switchwide mode is f2e f3

    vdc_id  vdc_name                          state               mac                 type        lc
    ------  --------                          -----               ----------          ---------   ------
    1       step-n7k-2                        active              8c:60:4f:75:53:41   Admin       None
    2       vdc1                              active              8c:60:4f:75:53:42   Ethernet    f2e f3
    3       vdc2                              active              8c:60:4f:75:53:43   Ethernet    f2e f3
    4       vdc3                              active              8c:60:4f:75:53:44   Ethernet    f2e f3
    6       vdc5                              active              8c:60:4f:75:53:46   Ethernet    f2e f3

    step-n7k-2#
    2016-04-04T02:19:29: %UNICON-INFO: +++ execute  +++

    2016-04-04T02:19:29: %UNICON-INFO: +++ exec switchto vdc vdc1 +++
    switchto vdc vdc1
    Cisco Nexus Operating System (NX-OS) Software
    TAC support: http://www.cisco.com/tac
    Copyright (c) 2002-2015, Cisco Systems, Inc. All rights reserved.
    The copyrights to certain works contained in this software are
    owned by other third parties and used and distributed under
    license. Certain components of this software are licensed under
    the GNU General Public License (GPL) version 2.0 or the GNU
    Lesser General Public License (LGPL) Version 2.1. A copy of each
    such license is available at
    http://www.opensource.org/licenses/gpl-2.0.php and
    http://www.opensource.org/licenses/lgpl-2.1.php
    step-n7k-2-vdc1#
    2016-04-04T02:19:31: %UNICON-INFO: +++ execute  +++

    2016-04-04T02:19:31: %UNICON-INFO: +++ exec term length 0 +++
    term length 0
    step-n7k-2-vdc1#
    2016-04-04T02:19:31: %UNICON-INFO: +++ execute  +++

    2016-04-04T02:19:31: %UNICON-INFO: +++ exec term width 511 +++
    term width 511
    step-n7k-2-vdc1#
    2016-04-04T02:19:31: %UNICON-INFO: +++ execute  +++

    2016-04-04T02:19:31: %UNICON-INFO: +++ exec terminal session-timeout 0 +++
    terminal session-timeout 0
    step-n7k-2-vdc1#
    2016-04-04T02:19:31: %UNICON-INFO: +++ config  +++
    config term
    Enter configuration commands, one per line.  End with CNTL/Z.
    step-n7k-2-vdc1(config)# no logging console
    step-n7k-2-vdc1(config)# line console
    step-n7k-2-vdc1(config-console)# exec-timeout 0
    step-n7k-2-vdc1(config-console)# terminal width 511
    step-n7k-2-vdc1(config-console)# end
    step-n7k-2-vdc1# Out[3]: 'vdc1'

You see a relatively longer output because every time it switches to a new VDC,
the terminal is reinitialized.

.. note::

    You don't need to `switchback` to execute this API. You can call `switchto`
    even when you are already inside a VDC. `switchback` is implicitly called.

switchback
-----------

It is just the opposite of `switchto`. It is used to return to the *default*
VDC. This service takes no mandatory arguments.

==========   ======================    =============================
Argument     Type                      Description
==========   ======================    =============================
timeout      int (10)                  timeout value for the overall interaction.
dialog       Dialog                    additional dialog
command      str (switchback)          alternate command.
==========   ======================    =============================

.. code-block:: python

    In [4]: con.switchback()
    2016-04-04T02:34:51: %UNICON-INFO: +++ switchback  +++
    2016-04-04T02:34:51: %UNICON-INFO: +++ execute  +++
    2016-04-04T02:34:51: %UNICON-INFO: +++ exec switchback +++
    switchback
    step-n7k-2#

.. note::

    If you call this API while being in a `default` VDC, then the
    call will be simply bypassed.

create_vdc
-----------

This service creates a VDC by name.

==========   ======================    =============================
Argument     Type                      Description
==========   ======================    =============================
vdc_name*    string                    name of the VDC to create.
timeout      int (120)                 timeout value for the overall interaction.
dialog       Dialog                    additional dialog
command      str (vdc)                 alternate command.
==========   ======================    =============================

::

    In [10]: con.create_vdc('vdc1')
    2016-04-04T02:49:49: %UNICON-INFO: +++ create vdc  +++
    2016-04-04T02:49:49: %UNICON-INFO: +++ None  +++
    2016-04-04T02:49:49: %UNICON-INFO: +++ execute  +++
    2016-04-04T02:49:49: %UNICON-INFO: +++ exec show vdc +++
    show vdc

    Switchwide mode is f2e f3

    vdc_id  vdc_name                          state               mac                 type        lc
    ------  --------                          -----               ----------          ---------   ------
    1       step-n7k-2                        active              8c:60:4f:75:53:41   Admin       None
    3       vdc2                              active              8c:60:4f:75:53:43   Ethernet    f2e f3
    4       vdc3                              active              8c:60:4f:75:53:44   Ethernet    f2e f3
    6       vdc5                              active              8c:60:4f:75:53:46   Ethernet    f2e f3

    step-n7k-2#
    2016-04-04T02:49:50: %UNICON-INFO: +++ config  +++
    config term
    Enter configuration commands, one per line.  End with CNTL/Z.
    step-n7k-2(config)# vdc vdc1
    Note:  Creating VDC, one moment please ...
    2016 Apr  3 14:52:30  %$ VDC-2 %$ %SYSLOG-2-SYSTEM_MSG : logflash ONLINE
    step-n7k-2(config-vdc)# end
    step-n7k-2# Out[10]: 'vdc1'

.. note::

    You can call this API from any VDC. It will create the VDC and again come
    back to the same VDC from which it was called.

delete_vdc
------------

This service can be used for deleting a vdc.

==========   ======================    =============================
Argument     Type                      Description
==========   ======================    =============================
vdc_name*    string                    name of the VDC to delete
timeout      int (90)                  timeout value for the overall interaction.
dialog       Dialog                    additional dialog
command      str (no vdc)              alternate command.
==========   ======================    =============================

::

    In [9]: con.delete_vdc('vdc1')

    2016-04-04T02:45:04: %UNICON-INFO: +++ delete vdc  +++
    2016-04-04T02:45:04: %UNICON-INFO: +++ None  +++
    2016-04-04T02:45:04: %UNICON-INFO: +++ execute  +++
    2016-04-04T02:45:04: %UNICON-INFO: +++ exec show vdc +++
    show vdc

    Switchwide mode is f2e f3

    vdc_id  vdc_name                          state               mac                 type        lc
    ------  --------                          -----               ----------          ---------   ------
    1       step-n7k-2                        active              8c:60:4f:75:53:41   Admin       None
    2       vdc1                              active              8c:60:4f:75:53:42   Ethernet    f2e f3
    3       vdc2                              active              8c:60:4f:75:53:43   Ethernet    f2e f3
    4       vdc3                              active              8c:60:4f:75:53:44   Ethernet    f2e f3
    6       vdc5                              active              8c:60:4f:75:53:46   Ethernet    f2e f3

    step-n7k-2#
    2016-04-04T02:45:05: %UNICON-INFO: +++ config  +++
    config term
    Enter configuration commands, one per line.  End with CNTL/Z.
    step-n7k-2(config)# no vdc vdc1
    Deleting this vdc will remove its config. Continue deleting this vdc (y/n)?  [no] yes
    Note:  Deleting VDC, Files under bootflash:/vdc_2/* will be deleted!  One moment please ...
    step-n7k-2(config)# end
    step-n7k-2# Out[9]: 'vdc1'

.. note::

    You can call `delete_vdc` even when you are inside a VDC. Only thing to
    take care is that you can't delete the same VDC in which you are already
    in. Isn't is obvious !!


reload
------

Service to reload the device.

Sometimes reload fails because device prompt is unable to match
due to console messages over terminal and this results in reload timeout.
In such a case `prompt_recovery` can be used to recover the device.

=======================   =======================     ========================================
Argument                  Type                        Description
=======================   =======================     ========================================
reload_command            str                         reload command to be issued on device.
                                                      default reload_command is "reload"
dialog                    Dialog                      additional dialogs/new dialogs which are not handled by default.
timeout                   int                         timeout value in sec, single-rp/dual-rp Default is 400/700 sec
prompt_recovery           bool (default False)        Enable/Disable prompt recovery feature
return_output             bool (default False)        Return namedtuple with result and reload command output
config_lock_retries       int (default 20)            retry times if config mode is locked
config_lock_retry_sleep   int (default 9 sec)         sleep between config_lock_retries
image_to_boot             str                         n9k plugin only: boot from specified image if device goes into loader state
reload_creds              list or str ('default')     Credentials to use if device prompts for user/pw.
reconnect_sleep           int (default 60 sec)        sleep time interval before reconnect device
=======================   =======================     ========================================

    return :
        * True on Success

        * raise SubCommandFailure on failure.

        * If return_output is True, return a namedtuple with result and reload command output

.. code-block:: python

        #Example
        --------

        rtr.reload()
        # If reload command is other than 'reload'
        rtr.reload(reload_command="reload location all", timeout=400)

        # using prompt_recovery option
        rtr.reload(prompt_recovery=True)

        # using return_output
        result, output = rtr.reload(return_output=True)


l2rib_dt
--------

Layer 2 Routing Information Base (L2RIB) developer tool service.

With this service, the l2rib tool can be used to execute commands. The service
is intended to be used as a context manager, see example below.

=======================   =======================     ===============================================
Argument                  Type                        Description
=======================   =======================     ===============================================
client_id                 int                         (optional) Client identifier for l2rib_dt tool.
                                                      By default, a random ID will be used.
=======================   =======================     ===============================================


.. code-block:: python

        # default client ID (random)
        with rtr.l2rib_dt() as l2rib:
            l2rib.execute('l2rib command')

        # specific client ID
        with rtr.l2rib_dt(client_id=1000) as l2rib:
            l2rib.execute('l2rib command')
