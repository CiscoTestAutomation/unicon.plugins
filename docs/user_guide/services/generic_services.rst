
Common Services
===============

Common services, as the name suggests, are applicable for all (most)
of the switch and router platforms. In this way we can cut down a lot
of document duplication across platforms. This section includes all
such services which are applicable on both HA and Non-HA platform.

There could be cases when a particular platform supports more services
than listed below or there could be some omissions as well. In that case
please refer to the platform specific service documentations. For example
NXOS supports `vdc` handling APIs which are not relevant on other platforms
line XR or IOS etc. Also in case of linux we only have `execute` service.

.. _controlled_settings:

**Error pattern handling**

If you want to execute services that could fail to execute properly and you want to verify
this automatically using a specific error pattern, you can specify the `error_pattern`
option with a list of regular expressions to match on the output. This option is available
for the execute service.

The regex pattern is matched using the python multiline option (re.M) so you can use
the start of line (`^`) character to match specific line output.

.. code-block:: python

    >>> c.execute('show interface invalid', error_pattern=['^% Invalid'])

If you want to avoid errors being detected with any command, you can set the settings object
`ERROR_PATTERN` to an empty list. The current generic default is an empty list.

.. code-block:: python

    >>> from pyats.topology import loader
    >>>
    >>> tb = loader.load('testbed.yaml')
    >>> ncs = tb.devices.ncs
    >>>
    >>> ncs.connect(via='cli')
    >>> ncs.settings.ERROR_PATTERN=[]

The default error patterns can be seen by printing the settings.ERROR_PATTERN attribute.

.. code-block:: python

    >>> ncs.settings.ERROR_PATTERN
    ['Error:', 'syntax error', 'Aborted', 'result false']

Alternatively, you can pass an empty list when executing a command to avoid error pattern checking.

.. code-block:: python

    >>> c.execute('show command error', error_pattern=[])

You can also append a pattern to the existing patterns defined in the settings when executing a command
(e.g. to add an error pattern for a specific command to execute).

.. code-block:: python

    >>> c.execute('show command error', append_error_pattern=['^specific error pattern'])


**EOF Exception handling**

If device connection is closed/terminated unexpectedly during service calling, we can reconnect
to device. EOF exception is raised by Spawn when connection is not available.

Sample usage:

.. code-block:: python

    from unicon.core.errors import EOF, SubCommandFailure
    try:
      d.execute(cmd) # or any service call.
    except SubCommandFailure as e:
      if isinstance(e.__cause__, EOF):
        print('Connection closed, try reconnect')
        d.disconnect()
        d.connect()

**Printing matched patterns**

If you want to print the dialog statements matched patterns during the run,
you need to set the log level to logging.DEBUG or connect with debug=True.

Default value is False.

.. code-block:: python

    >>> from pyats.topology import loader
    >>>
    >>> tb = loader.load('testbed.yaml')
    >>> uut = tb.devices['uut']
    >>>
    >>> uut.connect()
    >>> uut.log.setLevel(logging.DEBUG)

Alternative:

    >>> uut.connect(debug=True)


**Environment variables**

If you want to set environment variables for the connection, you can set them
by adding key-value pairs to the `ENV` dictionary.

.. code-block:: python

    >>> uut.settings.ENV = {'MYENV': 'mystring'}

**Terminal size settings**

To set the terminal size (rows, cols) you can use the `ROWS` and `COLUMNS`
environment variables. The default terminal size is 24 x 80. Some plugins
like linux and nxos/aci have their own defaults.

.. code-block:: python

    >>> uut.settings.ENV = {'ROWS': 200, 'COLUMNS': 200}

.. note ::

   Settings can also be patched in the testbed yaml file as shown :ref:`here<settings_control>`.


execute
-------

This service is used to execute arbitrary commands on the device. Though
it is tailor made to handle command which do not *interact* but by providing
additional dialogs you can handle those minor interactions.

This works seamlessly across both HA and Non-HA devices, but on HA platforms
in case you need to send commands to standby, you can do so by using the
`target` argument in `execute`. Please refer the code section below to check
that out.

Use `prompt_recovery` argument for using `prompt_recovery` feature.
Refer :ref:`prompt_recovery_label`  for details on prompt_recovery feature.

.. note::

    Not all platforms allow command execution on the standby RP as it
    may not be possible to unlock the standby RP.
    Please check before using this option.

For commands which have very long runtime, e.g `show run`, you can change
the timeout value using the `timeout` option. By default all the exec
commands have a timeout of 60 seconds.

`Execute` service returns the output of the command in the string format
or it raises an exception. If you pass a list of commands or
a multiline string, a dictionary is returned. You can expect a SubCommandFailure
error in case anything goes wrong.

If you want to pass a multiline string as a single command, you should pass
a list where the list item as a multiline string, see example below.


====================   ========================    ====================================================
Argument               Type                        Description
====================   ========================    ====================================================
timeout                int (default 60 sec)        timeout value for the command execution takes.
reply                  Dialog                      additional dialog
command                str                         command to execute on device handle
target                 standby/active              by default commands will be executed on active,
                                                   use target=standby to execute command on standby.
prompt_recovery        bool (default False)        Enable/Disable prompt recovery feature
error_pattern          list                        List of regex strings to check output for errors.
append_error_pattern   list                        List of regex strings append to error_pattern.
search_size            int (default 8K bytes)      maximum size in bytes to search at the
                                                   end of the buffer
allow_state_change     bool (default False)        By default, end state should be same as start state.
                                                   If True, end state can be any valid state.
service_dialog         Dialog                      service_dialog overrides the execute service
                                                   dialog.
matched_retries        int (default 1)             retry times if statement pattern is matched
matched_retry_sleep    float (default 0.05 sec)    sleep between matched_retries
====================   ========================    ====================================================

By default, device start state should be same as end state. For example, if we
use `execute()` service when device is at enable state then after running the command,
device should come back to enable state. If any state change occurs then `StateMachineError`
exception is raised. This behavior can be change by using `allow_state_change=True` argument.
With `allow_state_change=True`, after running the command, it will be valid if device comes
to any valid state. Valid states are all defined states in the plugin specific statemachine.

The search size option specifies the maximum size at the end of the buffer
to search for the prompt and other patterns (e.g. from the reply Dialog).
Specify 0 to search the complete buffer. The search size option is used to
speed up pattern matching against the buffer. The default search size should
be sufficient for most needs and allows large outputs to be processed more efficiently.

A default set of statements is included in the dialog for the
execute service. You can find the default dialog patterns here: `Service dialogs`_.
You can add additional dialogs to the services dialogs by using the `reply` parameter.

.. _service dialogs: service_dialogs.html

You can pass the `service_dialog` option to the execute() service to override the execute service dialogs.
This is useful if the execute service patterns are causing problems, e.g. the ``Username:`` prompt
is responded to by default with the login credentials. In some cases this leads to false positive
pattern responses.

Example usage of the execute service:

.. code-block:: python

        #Example
        --------

        # simple execute call
        output = rtr.execute("show clock")

        # changing the timeout value
        output = rtr.execute("show logging", timeout=200)

        # sending command to standby rp
        output = rtr.execute("show clock", target='standby')

        # using the reply option.
        from unicon.eal.dialogs import Statement, Dialog
        dialog = Dialog([
            Statement(pattern=r'.*Do you wish to proceed anyway\? \(y/n\)\s*\[n\]',
                                action='sendline(y)',
                                loop_continue=True,
                                continue_timer=False)
        ])
        rtr.execute("write erase", reply=dialog)

        # using prompt_recovery option
        output = rtr.execute("show clock", prompt_recovery=True)

        # clear command (default response of '\r' to confirm prompt)
        rtr.execute('clear logging')

        # Check output for errors
        rtr.execute('show interface TokenRing0/0', error_pattern=['^% Invalid'])

        # Execute multiline command by passing a list with a multiline string.
        rtr.execute(['line1\nline2\nline3'])

        # Allowing state changes
        # Below will work
        d.execute('config term', allow_state_change=True)
        # Below will raise exception
        d.execute('config term')

        # Override the execute service dialog
        d.execute('show wireless client mac-address 00-11-22-33-44-55 detail', service_dialog=None)


configure
---------

Service to configure device with list of `commands`. Config without
config_command will take device to config mode. Commands Should be list,
if `config_command` are more than one. reply option can be passed for the
interactive config command. Command will be executed on standby if target
is specified as standby. Use `prompt_recovery` argument for using
`prompt_recovery` feature. Refer :ref:`prompt_recovery_label`  for details
on prompt_recovery feature.


====================  =======================    ========================================
Argument              Type                       Description
====================  =======================    ========================================
timeout               int                        timeout value for the command execution takes.
error_pattern         list                       List of regex strings to check output for errors.
append_error_pattern  list                        List of regex strings append to error_pattern.
reply                 Dialog                     additional dialog
command               list                       list of commands to configure
prompt_recovery       bool (default False)       Enable/Disable prompt recovery feature
force                 bool (default False)       For XR, run commit force at end of config.
replace               bool (default False)       For XR, run commit replace at end of config.
lock_retries          int (default 0)            retry times if config mode is locked
lock_retry_sleep      int (default 2 sec)        sleep between lock_retries
target                str (default "active")     Target RP where to execute service, for DualRp only
bulk                  bool (default False)       If False, send all commands in one sendline. If True, send commands in chunked mode
bulk_chunk_lines      int (default 50)           maximum number of commands to send per chunk, 0 means to send all commands in a single chunk
bulk_chunk_sleep      float (default 0.5 sec)    sleep between sending command chunks
====================  =======================    ========================================



.. code-block:: python

        #Example
        --------

        output = rtr.configure()
        output = rtr.configure("no logging console")
        cmd =["hostname si-tvt-7200-28-41", "no logging console"]
        output = rtr.configure(cmd)
        output = rtr.configure(cmd, target='standby')

        #For XR:
        -------
        rtr.configure(cmd, force=True)
        rtr.configure(cmd, replace=True)

For `(os='iosxe', platform='sdwan')` plugin, `configure()` service issue `config-transaction`
command in place of `'config term` and run `commit` command before moving out of config mode.

..  code-block:: python

        #configure() service on iosxe/sdwan plugin.
        >>> d.configure('no logging console')
        [2019-05-22 17:38:58,981] +++ Router: config +++
        config-transaction
        admin connected from 127.0.0.1 using console on Router
        Router(config)#no logging console
        Router(config)#commit
        % No modifications to commit.
        Router(config)#end
        Router#
        'no logging console\r\ncommit\r\n% No modifications to commit.\r\n'
        >>>


send
----
Service to  send the **'command/string'** with "\r" to spawned channel. If
target is passed as standby, command will be sent to standby spawn .

    arg  :
        * command = <Command to be sent>"\r"

        * target='standby'

    return :
        * True on Success, raise SubCommandFailure on failure.

.. code-block:: python

        Example ::

            rtr.send("show clock\r")
            rtr.send("show clock\r", target='standby')


transmit
--------
Service similar to `send()`.

.. code-block:: python

        Example ::

            rtr.transmit("show clock\r")
            rtr.transmit("show clock\r", target='standby')


sendline
--------
Service to  send the **'command/string'** to spawned channel, "\r" will be
appended to command by sendline. If  target is passed as standby, command will
be sent to standby spawn .

arg  :
    * command = <Command to be sent>

    * target='standby'

return :
    * True on Success, raise SubCommandFailure on failure.

.. code-block:: python

    Example ::

        rtr.sendline("show clock")
        rtr.sendline("show clock", target='standby')


expect
------
Match a list of patterns against the buffer. If target is passed as standby,
patterns matches against the buffer on standby spawn channel.

===========   ===========    ========================================
Argument      Type                      Description
===========   ===========    ========================================
patterns      list           list of patterns
timeout       int            timeout in sec (default 10 seconds).
size          int            read size in bytes for reading the buffer
target        str            'standby' to match a list of patterns against
                             the buffer on standby spawn channel.
trim_buffer   bool           trim the buffer after a successful match or not
search_size   int            maximum size in bytes to search at the
                             end of the buffer (default 8K bytes)
===========   ===========    ========================================

Default search size is 8K, use 0 to search the complete buffer.

  return :

          ExpectMatch instance.
            * It contains the index of the pattern that matched.
            * matched string.
            * re match object.

  raises:
            TimeoutError: In case no match is found within the timeout period
                or raise SubCommandFailure on failure.

.. code-block:: python

          Example ::

            rtr.sendline("a command")
            rtr.expect([r'^pat1', r'pat2'], timeout=10, target='standby')


receive
-------
Service for matching a pattern from buffer. If target is passed as standby,
patterns matches against the buffer on standby spawn channel.

If provided pattern is `r'nopattern^'` then all data till timeout period will
be matched and can be retrieved using the `receive_buffer()` service.

===========   ===========    ========================================
Argument      Type                      Description
===========   ===========    ========================================
pattern       str            regular expression patterns
timeout       int            timeout in sec (default 10 seconds).
size          int            read size in bytes for reading the buffer
target        str            'standby' to match a list of patterns against
                             the buffer on standby spawn channel.
trim_buffer   bool           trim the buffer after a successful match or not
search_size   int            maximum size in bytes to search at the
                             end of the buffer (default 8K bytes)
===========   ===========    ========================================

Default search size is 8K, use 0 to search the complete buffer.

  return :
           * Bool: True or False
           * True: If data is matched by provided pattern.
           * False: If nothing is matched by pattern or if `r'nopattern^'` pattern is used.
           * Data matched by pattern is can be retrieved by using the `receive_buffer()` service.

  raises:
           * No Exception is raised if pattern does not get matched or timeout happens.
           * `SubCommandFailure` will be raised if any Exception is raised apart from `TimeoutError`.

.. code-block:: python

          Example ::

            rtr.transmit("a command")
            rtr.receive(r'^pat1', timeout=10, target='standby')


receive_buffer
--------------
Service to get data match by `receive()` service pattern. This service should be invoked only
after calling `receive()` service, else `SubCommandFailure` exception will be raised.

This service takes no arguments.

    Returns:
        String: Data matched by `receive()` service pattern.

.. code-block:: python

          Example ::

            rtr.transmit("a command")
            rtr.receive(r'^pat1', timeout=10, target='standby')
            output = rtr.receive_buffer()


expect_log
----------
This service is removed. Please use Connection logger setLevel API 
to enable/disable internal debug logging.

.. code-block:: python

          Example ::

            rtr.connect()
            rtr.log.setLevel(logging.DEBUG)


log_user
--------
Service to enable or disable a device logs on screen.

  args

    * enable = True/False

  .. code-block:: python

        Example ::

          rtr.log_user(enable=True)
          rtr.log_user(enable=False)


log_file
--------
Service to get or change Device `FileHandler` file.
If no argument passed then it return current filename of `FileHandler`.
Return `True`, if file handler updated with new filename.

  args

    * filename: file name in which device logs to dump.

  .. code-block:: python

        Example ::

          rtr.log_file(filename='/some/path/uut.log')
          rtr.log_file() # Returns current FileHandler filename


enable
------

Service to change the device mode to enable from any state. Brings the standby
handle to enable state, if standby is passed as input.
If command is given, it will be issued on the device to become in enable mode.

    arg :
        * target='standby'
        * command='enable 7'

    return :
        * True on Success, raise SubCommandFailure on failure.

.. code-block:: python

        #Example
        --------

        rtr.enable()
        rtr.enable(target='standby')
        rtr.enable(command='enable 7')


disable
-------

Service to change the device to disable mode from any state. Brings the standby
handle to disable state, if standby is passed as input.

     arg :
        * target='standby'

     return :
        * True on Success, raise SubCommandFailure on failure.

.. code-block:: python

        #Example
        --------

        rtr.disable()
        rtr.disable(target='standby')


ping
----

Service to issue ping response request to another network from device.


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
ping_packet_timeout         ping packet timeout in seconds
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

        output = ping(addr="9.33.11.41")
        output = ping(addr="10.2.1.1", extd_ping='yes')


switchto
--------

The `switchto` service is a helper method to switch between CLI states. This can be used to switch
to known states in the statemachine, e.g. 'enable' or 'rommon' (if supported by the plugin).

===================   ========================    ====================================================
Argument              Type                        Description
===================   ========================    ====================================================
to_state              str or list                 target state(s) to switch to
timeout               int (default 60 sec)        timeout value for the command execution takes.
===================   ========================    ====================================================

.. code-block:: python

        #Example
        --------

        >>> dev.state_machine.states
        [disable, enable, config, rommon, shell]
        >>>
        >>> dev.switchto('config')

        %UNICON-INFO: +++ switchto: config +++
        config term
        R1(conf)#
        >>>



traceroute
----------

Service to issue traceroute.

        traceroute_options = ['proto', 'ingress', 'source', 'dscp', 'numeric',
                              'timeout', 'probe', 'minimum_ttl', 'maximum_ttl',
                              'port', 'style' ]


=====================       ===============================================================
Argument                    Description
=====================       ===============================================================
addr                        Destination address
proto                       protocol(ip/ipv6)
ingress                     Ingress traceroute
source                      Source address or interface
dscp                        DSCP Value
numeric                     Numeric display
timeout                     Timeout in seconds
probe                       Probe count
minimum_ttl                 Minimum Time to Live
maximum_ttl                 Maximum Time to Live
port                        Port Number
style                       Loose, Strict, Record, Timestamp, Verbose
=====================       ===============================================================


    return :
        * traceroute command response on Success

        * raise SubCommandFailure on failure.

.. code-block:: python

        #Example
        --------

        output = traceroute(addr="9.33.11.41")
        output = traceroute(addr="10.2.1.1", maximum_ttl=3)

copy
----

Service to support variants of the IOS copy command, which basically
copies images and configs into and out of router Flash memory.


===============     ===============================================================
Argument            Description
===============     ===============================================================
source              filename/device partition/remote type ( i.e image.bin/disk0:/scp:)
source_file         source file name in device disk/tftp (file name with path)
dest                destination filename/device partition/remote type( i.e startup-config/disk0:/scp:)
dest_file           destination file name on device disk / tftp (file name with path)
dest_directory      destination directory for wildcard copy
server              tftp/ftp server address or a name known to DNS
user                tftp/ftp/scp username for image copy
password            tftp/ftp/scp password for image copy.  May be specified as a :ref:`secret string<secret_strings>` device credential.
vrf                 VRF interface name
erase               (y\n) whether or not to erase Flash memory before copying. default value is n.
partition           used for dual-Flash routers. Specifies the Flash partition number to copy the router image to. If this option is not specified, the default partition provided is 0.
overwrite           overwrite the file if exists. Default value is True
timeout             Copy timeout in sec
net_type            host|network type of remote server
max_attempts        Copy at most this many times if a copy fails for any reason.
reply               Additional Dialog which are not handled by default.
extra_options       Additional platform dependent options to append to the copy command.
===============     ===============================================================


    return :
        * Copy command response on Success

        * raise SubCommandFailure on failure.

    .. code-block:: python

        #Example
        --------

        out = rtr.copy(source='running-conf',
                       dest='startup-config')

        copy_input = {'source' :'tftp:',
                      'dest':'disk0:',
                      'source_file' : 'copy-test',
                      'dest_file':'copy-test',
                      'erase':'y',}
        out = rtr.copy(copy_input)

        out = rtr.copy(source = 'tftp:',
                       dest = 'bootflash:',
                       source_file  = 'copy-test',
                       dest_file = 'copy-test',
                       server='10.105.33.158')


reload
------

Service to reload the device.

Sometimes reload fails because device prompt is unable to match
due to console messages over terminal and this results in reload timeout.
In such a case `prompt_recovery` can be used to recover the device.
Refer :ref:`prompt_recovery_label` for details on prompt_recovery feature.

===============   =======================     ================================================================================
Argument          Type                        Description
===============   =======================     ================================================================================
reload_command    str                         reload command to be issued on device.
                                              default reload_command is "reload"
reply             Dialog                      additional dialogs/new dialogs which are not handled by default.
timeout           int                         timeout value in sec, Default Value is 300 sec
reload_creds      list or str ('default')     Credentials to use if device prompts for user/pw.
prompt_recovery   bool (default False)        Enable/Disable prompt recovery feature
return_output     bool (default False)        Return namedtuple with result and reload command output
                                              This option is available for generic, nxos and iosxe/cat3k (single rp) plugin.
image_to_boot     str                         Image to boot from rommon. Available for iosxe/cat3k and iosxe/cat9k
===============   =======================     ================================================================================

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

.. note::

        Default reload timeout values are

            single-rp generic = 300 sec

            single-rp nxos    = 400 sec

            dual-rp generic   = 500 sec

            dual-rp nxos      = 600 sec


bash_console
------------

Service to execute commands in the router Bash. ``bash_console``
gives you a router-like object to execute commands on using python context
managers.

==========   ======================    ========================================
Argument     Type                      Description
==========   ======================    ========================================
timeout      int (default 60 sec)      timeout in sec for executing commands
target       str                       'standby' to bring standby console to bash.
==========   ======================    ========================================

.. code-block:: python

    with device.bash_console() as bash:
        output1 = bash.execute('ls')
        output2 = bash.execute('pwd')

    # To run bash on standby console.
    with device.bash_console(target='standby') as bash:
        output1 = bash.execute('ls', target='standby')
        output2 = bash.execute('pwd', target='standby' )



guestshell
----------

Service to execute commands in the Linux "guest shell" available on certain
NXOS and IOSXE platforms. ``guestshell`` gives you a router-like object to execute
commands on using a Python context manager.

=================   ========   ===================================================================
Argument            Type       Description
=================   ========   ===================================================================
enable_guestshell   boolean    Explicitly enable the guestshell before attempting to enter.
timeout             int (10)   Timeout for "guestshell enable", "guestshell", and "exit" commands.
retries             int (20)   Number of retries (x 5 second interval) to attempt to enable guestshell.
=================   ========   ===================================================================

.. code-block:: python

    with device.guestshell(enable_guestshell=True, retries=30) as gs:
        output = gs.execute("ifconfig")

    with device.guestshell() as gs:
        output1 = gs.execute('pwd')
        output2 = gs.execute('ls -al')




Dual RP Services
================

In addition to the common services, following are applicable only for only
*dual-rp* or *ha* platforms.

get_mode
--------

Service to get the redundancy mode of the device.

    arg :
        * None

    return :
        * 'sso', 'rpr', ''('if  not able to identify the mode')

        * raise SubCommandFailure on failure.

.. code-block:: python

        #Example
        --------

        mode = rtr.get_mode()


get_rp_state
------------

Service to get the redundancy state of the device rp. Returns  standby rp
state if standby is passed as input.


    arg :
        * target=standby

    return :
        * Expected return values are ACTIVE, STANDBY COLD, STANDBY HOT

        * raise SubCommandFailure on failure.

.. code-block:: python

        #Example
        --------

        rtr.get_rp_state()
        rtr.get_rp_state(target='standby')


get_config
----------

Service return running configuration of the device.
        Returns  standby running configuration if standby is passed as input.


        arg :
            * target='standby'

        return :
            * running configuration on Success ,

            * raise SubCommandFailure on failure.

.. code-block:: python

        #Example
        --------
        rtr.get_config()
        rtr.get_config(target='standby')


guestshell
----------

Service to execute commands in the Linux "guest shell" available on certain
NXOS and IOSXE platforms. ``guestshell`` gives you a router-like object to execute
commands on using a Python context manager.

=================   ========   ===================================================================
Argument            Type       Description
=================   ========   ===================================================================
enable_guestshell   boolean    Explicitly enable the guestshell before attempting to enter.
timeout             int (10)   Timeout for "guestshell enable", "guestshell", and "exit" commands.
retries             int (20)   Number of retries (x 5 second interval) to attempt to enable guestshell.
=================   ========   ===================================================================

.. code-block:: python

    with device.guestshell(enable_guestshell=True, retries=30) as gs:
        output = gs.execute("ifconfig")

    with device.guestshell() as gs:
        output1 = gs.execute('pwd')
        output2 = gs.execute('ls -al')


sync_state
----------

Service to bring the device to stable and re-designate the handles role.

    arg :
        * None

    return :
        * True on Success,

        * Raises SubcommandFailure exception on failure

.. code-block:: python

        #Example
        --------
                rtr.sync_state()


switchover
----------

Service to switchover the device.

Refer :ref:`prompt_recovery_label` for details on `prompt_recovery` argument.


================   =======================     =========================================================================
Argument           Type                        Description
================   =======================     =========================================================================
command            str                         switchover command to be issued on device.
                                               default command is "redundancy force-switchover"
reply              Dialog                      additional dialogs/new dialogs which are not handled by default.
timeout            int                         timeout value in sec, Default Value is 500 sec
sync_standby       boolean                     Flag to decide whether to wait for standby to be UP or Not. default: True
prompt_recovery    boolean                     Enable/Disable prompt recovery feature. Default is False.
switchover_creds   list or str ('default')     Credentials to use if device prompts for user/pw.
================   =======================     =========================================================================

 return :
    * True on Success

    * raise SubCommandFailure on failure.


.. code-block:: python

    Example ::

    rtr.switchover()

    # If switchover command is other than 'redundancy force-switchover'
    rtr.switchover(command="command which invoke switchover",
                   timeout=700)
    # Switchover and not wait for standby to
    rtr.switchover(sync_standby=False)

    # using prompt_recovery option
    rtr.switchover(prompt_recovery=True)


reset_standby_rp
----------------

Service to reset the standby rp.

===============   ==========    ========================================
Argument          Type          Description
===============   ==========    ========================================
command           str           command to be issued on device.
                                default command is "redundancy reload peer"
reply             Dialog        additional dialogs/new dialogs which are not handled by default.
timeout           int           timeout value in sec, Default Value is 500 sec

===============   ==========    ========================================

  return :

    * True on Success

    * raise SubCommandFailure on failure.

.. code-block:: python

    Example ::

      rtr.reset_standby_rp()

      # If command is other than 'redundancy reload peer'
      rtr.reset_standby_rp(command="command which invoke reload on standby-rp",
                           timeout=600)



Stack RP Services
=================

In addition to the common services, following are applicable only for
*ha* platforms with *stack* RP.


get_rp_state
------------

Service to get the redundancy state of the device rp. Returns peer rp
state if peer rp alias is passed as input.


==========   ======================    ========================================
Argument     Type                      Description
==========   ======================    ========================================
target       str                       target rp to check rp state. Default value is `active`
timeout      int (default 60 sec)      timeout in sec for executing commands
==========   ======================    ========================================

return :

    * Target rp state on Success. Possible states ACTIVE, STANDBY, MEMBER

    * raise SubCommandFailure on failure.

.. code-block:: python

        #Example
        --------

        rtr.get_rp_state()
        rtr.get_rp_state(target='standby')


switchover
----------

Service to switchover the stack device.

Refer :ref:`prompt_recovery_label` for details on `prompt_recovery` argument.


===============   =======================     ========================================
Argument          Type                        Description
===============   =======================     ========================================
command           str                         switchover command to be issued on device.
                                              default command is "redundancy force-switchover"
reply             Dialog                      additional dialogs/new dialogs which are not handled by default.
timeout           int                         timeout value in sec, Default Value is 600 sec
prompt_recovery   boolean                     Enable/Disable prompt recovery feature. Default is False.
===============   =======================     ========================================

 return :
    * True on Success

    * raise SubCommandFailure on failure.


.. code-block:: python

    Example ::

    rtr.switchover()

    # If switchover command is other than 'redundancy force-switchover'
    rtr.switchover(command="command which invoke switchover",
                   timeout=700)

    # using prompt_recovery option
    rtr.switchover(prompt_recovery=True)


reload
------

Service to reload the stack device.

===============   =======================     ========================================
Argument          Type                        Description
===============   =======================     ========================================
reload_command    str                         reload command to be issued on device.
                                              default reload_command is "redundancy reload shelf"
reply             Dialog                      additional dialogs/new dialogs which are not handled by default.
timeout           int                         timeout value in sec, Default Value is 900 sec
image_to_boot     str                         image to boot from rommon state
prompt_recovery   bool (default False)        Enable/Disable prompt recovery feature
return_output     bool (default False)        Return namedtuple with result and reload command output
raise_on_error    bool (default: True)        Raise exception on error
===============   =======================     ========================================

    return :
        * True on Success

        * raise SubCommandFailure on failure.

        * If return_output is True, return a namedtuple with result and reload command output

.. code-block:: python

        #Example
        --------

        rtr.reload()
        # If reload command is other than 'redundancy reload shelf'
        rtr.reload(reload_command="reload location all", timeout=400)

        # using prompt_recovery option
        rtr.reload(prompt_recovery=True)

        # using return_output
        result, output = rtr.reload(return_output=True)



Quad RP Services
================

In addition to the common services, following are applicable only for
*ha* platforms with *quad* RP.


get_rp_state
------------

Service to get the redundancy state for the quad rp device. Returns target rp
state if target is passed as input.


==========   ======================    ========================================
Argument     Type                      Description
==========   ======================    ========================================
target       str                       target rp to check rp state. Default value is `active`
timeout      int (default 60 sec)      timeout in sec for executing commands
==========   ======================    ========================================

return :

    * Target rp state on Success. Possible states ACTIVE, STANDBY, MEMBER, IN_CHASSIS_STANDBY

    * raise SubCommandFailure on failure.

.. code-block:: python

        #Example
        --------

        rtr.get_rp_state()
        rtr.get_rp_state(target='standby')


switchover
----------

Service to switchover the quad rp device.

Refer :ref:`prompt_recovery_label` for details on `prompt_recovery` argument.


===============   =======================     ========================================
Argument          Type                        Description
===============   =======================     ========================================
command           str                         switchover command to be issued on device.
                                              default command is "redundancy force-switchover"
reply             Dialog                      additional dialogs/new dialogs which are not handled by default.
timeout           int                         timeout value in sec, Default Value is 600 sec
sync_standby      boolean                     Flag to decide whether to wait for standby to be UP or Not. default: True
prompt_recovery   boolean                     Enable/Disable prompt recovery feature. Default is False.
===============   =======================     ========================================

 return :
    * True on Success

    * raise SubCommandFailure on failure.


.. code-block:: python

    Example ::

    rtr.switchover()

    # If switchover command is other than 'redundancy force-switchover'
    rtr.switchover(command="command which invoke switchover",
                   timeout=700)

    # Switchover and not wait for standby to
    rtr.switchover(sync_standby=False)

    # using prompt_recovery option
    rtr.switchover(prompt_recovery=True)


reload
------

Service to reload the quad rp device.

===============   =======================     ========================================
Argument          Type                        Description
===============   =======================     ========================================
reload_command    str                         reload command to be issued on device.
                                              default reload_command is "reload"
reply             Dialog                      additional dialogs/new dialogs which are not handled by default.
timeout           int                         timeout value in sec, Default Value is 900 sec
prompt_recovery   bool (default False)        Enable/Disable prompt recovery feature
return_output     bool (default False)        Return namedtuple with result and reload command output
===============   =======================     ========================================

    return :
        * True on Success

        * raise SubCommandFailure on failure.

        * If return_output is True, return a namedtuple with result and reload command output

.. code-block:: python

        #Example
        --------

        rtr.reload()
        # If reload command is other than 'reload'
        rtr.reload(reload_command="reload location all", timeout=600)

        # using prompt_recovery option
        rtr.reload(prompt_recovery=True)

        # using return_output
        result, output = rtr.reload(return_output=True)
