Linux
=====

This section lists the services which are supported on Linux.

** Prompt and Shell Prompt overriding **

By default, Unicon is able to detect most variations of the bash shell prompt. However, in
instances where another shell is being used (such as `zsh` or `fish`) it may have difficulty
in detecting your prompt thus leaving the connection hanging. In the event this occurs you
can override your prompt using the `PROMPT` setting in your testbed file like so:

.. code-block:: yaml

    devices:
      linux_device:
        connections:
          cli:
            settings:
              PROMPT: '<your_prompt_regex>'

If `learn_hostname` is set to True, Unicon will attempt to learn and store the hostname
of you device in memory and switch the prompt to accommodate for that. It too can be overridden 
with the `SHELL_PROMPT` setting like so:

.. code-block:: yaml

    devices:
      linux_device:
        connections:
          cli:
            settings:
              SHELL_PROMPT: '<your_prompt_regex>'

Use `%N` in your regex to specify where the hostname should be located. 

execute
-------

This service is used to execute arbitrary commands on the device. Though it is
intended to execute non-interactive commands. In case you wanted to execute
interactive command use `reply` option. Refer :ref:`prompt_recovery_label` for
details on `prompt_recovery` argument.


===============   ======================    ========================================
Argument          Type                      Description
===============   ======================    ========================================
timeout           int (default 60 sec)      timeout value for the overall interaction.
reply             Dialog                    additional dialog
command           str                       command to execute
prompt_recovery   bool (default False)      Enable/Disable prompt recovery feature
check_retcode     bool (default False)      Enable/disable return code check
valid_retcodes    list (default [0])        Valid return codes
===============   ======================    ========================================

`Execute` service returns the output of the command in the string format
or it raises an exception. You can expect a TimeoutError or SubCommandFailure
error in case anything goes wrong.

This list of valid return codes can be specified via ``valid_retcodes``. If the setting
`CHECK_RETURN_CODE` is set to ``True`` or the ``check_retcode`` option is True,
the command `echo $?` is used to check the return value of the (last) executed command.
If the value is not in the list, a SubCommandFailure is raised.

You can enable return code checking by setting `CHECK_RETURN_CODE` to ``True``. By default,
return code checking is disabled.

.. code-block:: python

        #Example
        --------

        from unicon import Connection
        host=Connection(hostname='HOSTNAME',
                        start=['ssh lshekhar-bgl'],
                        credentials={'default': {'username': 'admin', 'password': 'cisco123'}},
                        os='linux')

        # simple execute call
        out = host.execute("ipconfig")

        # command which take longer time , with timeout value
        output = host.execute("ls -l", timeout=100)

        # using the reply option.
        from unicon.eal.dialogs import Statement, Dialog
        dialog = Dialog([
                       Statement(pattern=r'--More--',
                                action='sendline(q)',
                                loop_continue=True,
                                continue_timer=False)
                        ])
        output = host.execute("ps -ef | more", reply=dialog)

        # using prompt_recovery feature
        host.execute(cmd, prompt_recovery=True)


        # return code checking
        host.execute('command', valid_retcodes=[0], check_retcode=True)

        # Do not check return codes
        host.settings.CHECK_RETURN_CODE = False



ping
----

This service is used to ping another device from the linux command prompt. 
The addr argument is required, all other arguments are optional. By default,
a `count` of ``5`` is used.

The command `ping` is used by default. If the IP address is an IPv6 address,
`ping6` will be used automatically.

Argument options are translated to the ping command line options automatically.

===============   ======================    =========================================
Argument          Type                      Description
===============   ======================    =========================================
addr              string                    ping destination IP address. (required)
command           string                    command to execute (default: ping,
                                            ping6 will be used for IPv6 addr target)
options           string                    boolean options (see below).
count             integer/string            Number of packets to send.
interval          integer/string            Wait interval seconds between sending 
                                            each packet.
interface         string                    Set source address to specified 
                                            interface address. Argument may be 
                                            numeric IP address or  name of device.
pattern           string                    You may specify up to 16 pad bytes to 
                                            fill out the packet you send.
tos               integer                   Set Quality of Service related bits. 
                                            tos can be either decimal or hex number. 
size              integer/string            Specifies the number of data bytes to 
                                            be sent.
ttl               integer/string            Set the IP Time to Live.
timestamp         string                    Set special IP timestamp options. 
                                            timestamp option may be either
                                            tsonly (only timestamps),
                                            tsandaddr (timestamps and addresses) or
                                            tsprespec host1 [host2 [host3 [host4]]]
                                            (timestamp prespecified hops).
timeout           integer/string            Specify a timeout, in seconds.
error_pattern     list of regex             Error patterns that raise an exception.
                                            Default `['[123456789]+0*% packet loss']`
===============   ======================    =========================================

    return :
        * ping command response on Success

        * raise SubCommandFailure if error pattern is found

Boolean options

By default, the adaptive ping option (`A`) is used. To disable adaptive ping,
specify the `options` argument without the `A` option.

====  ==============================================================================================
Flag  Description
====  ==============================================================================================
A     Adaptive ping. Interpacket interval adapts to round-trip time
b     Allow pinging a broadcast address.
f     Flood ping.
L     Suppress loopback of multicast packets.
      This flag only applies if the ping destination is a multicast address.
n     Numeric output only. No attempt will be made to lookup symbolic names for host addresses.
q     Quiet output. Nothing is displayed except the summary lines at startup time and when finished.
r     Bypass the normal routing tables and send directly to a host on an attached interface.
R     Record route.
S     Set socket sndbuf. If not specified, it is selected to buffer not more than one packet.
U     Print full user-to-user latency
v     Verbose output.
====  ==============================================================================================


Example commands:

.. code-block:: python

    dev.ping(addr="127.0.0.1")
    dev.ping("127.0.0.1")
    dev.ping("::1", count=10)
    dev.ping("127.0.0.1", options="Av")
    dev.ping("127.0.0.1", size=1500)
    dev.ping('2.2.2.2', error_pattern=[])
    dev.ping('127.0.0.1', error_pattern=[' 0% packet loss'])


**Example output**

Example with `addr` parameter.

.. code-block:: python

    >>> r = l.ping(addr="127.0.0.1")
    ping -c5 -A 127.0.0.1
    PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
    64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.018 ms
    64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.022 ms
    64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.022 ms
    64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.024 ms
    64 bytes from 127.0.0.1: icmp_seq=5 ttl=64 time=0.029 ms

    --- 127.0.0.1 ping statistics ---
    5 packets transmitted, 5 received, 0% packet loss, time 801ms
    rtt min/avg/max/mdev = 0.018/0.023/0.029/0.003 ms, ipg/ewma 200.425/0.020 ms


Example with IP address string as parameter.

.. code-block:: python

    >>> r = l.ping("127.0.0.1")
    ping -c5 -A 127.0.0.1
    PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
    64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.015 ms
    64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.032 ms
    64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.028 ms
    64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.024 ms
    64 bytes from 127.0.0.1: icmp_seq=5 ttl=64 time=0.030 ms

    --- 127.0.0.1 ping statistics ---
    5 packets transmitted, 5 received, 0% packet loss, time 813ms
    rtt min/avg/max/mdev = 0.015/0.025/0.032/0.008 ms, ipg/ewma 203.271/0.020 ms
    cisco@server:~$ 


Example with IPv6 address as and count parameters.

.. code-block:: python

    >>> r = l.ping("::1", count=10)
    ping6 -c10 -A ::1
    PING ::1(::1) 56 data bytes
    64 bytes from ::1: icmp_seq=1 ttl=64 time=0.019 ms
    64 bytes from ::1: icmp_seq=2 ttl=64 time=0.032 ms
    64 bytes from ::1: icmp_seq=3 ttl=64 time=0.032 ms
    64 bytes from ::1: icmp_seq=4 ttl=64 time=0.018 ms
    64 bytes from ::1: icmp_seq=5 ttl=64 time=0.037 ms
    64 bytes from ::1: icmp_seq=6 ttl=64 time=0.032 ms
    64 bytes from ::1: icmp_seq=7 ttl=64 time=0.027 ms
    64 bytes from ::1: icmp_seq=8 ttl=64 time=0.036 ms
    64 bytes from ::1: icmp_seq=9 ttl=64 time=0.041 ms
    64 bytes from ::1: icmp_seq=10 ttl=64 time=0.200 ms

    --- ::1 ping statistics ---
    10 packets transmitted, 10 received, 0% packet loss, time 1807ms
    rtt min/avg/max/mdev = 0.018/0.047/0.200/0.051 ms, ipg/ewma 200.843/0.049 ms
    cisco@server:~$ 


Example with boolean options specified.

.. code-block:: python

    >>> r = l.ping("127.0.0.1", options="Av")
    ping -c5 -v -A 127.0.0.1
    PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
    64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.013 ms
    64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.052 ms
    64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.028 ms
    64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.027 ms
    64 bytes from 127.0.0.1: icmp_seq=5 ttl=64 time=0.028 ms

    --- 127.0.0.1 ping statistics ---
    5 packets transmitted, 5 received, 0% packet loss, time 801ms
    rtt min/avg/max/mdev = 0.013/0.029/0.052/0.013 ms, ipg/ewma 200.362/0.021 ms
    cisco@server:~$ 


Example with packet size specified.

.. code-block:: python

    >>> r = l.ping("127.0.0.1", size=1500)
    ping -c5 -s1500 -A 127.0.0.1
    PING 127.0.0.1 (127.0.0.1) 1500(1528) bytes of data.
    1508 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.017 ms
    1508 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.043 ms
    1508 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.032 ms
    1508 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.037 ms
    1508 bytes from 127.0.0.1: icmp_seq=5 ttl=64 time=0.028 ms

    --- 127.0.0.1 ping statistics ---
    5 packets transmitted, 5 received, 0% packet loss, time 801ms
    rtt min/avg/max/mdev = 0.017/0.031/0.043/0.010 ms, ipg/ewma 200.374/0.024 ms
    cisco@server:~$ 


Example with default exception on packet loss.

.. code-block:: python

    >>> r = c.ping('2.2.2.2')
    ping -A -c5 2.2.2.2
    PING 2.2.2.2 (2.2.2.2) 56(84) bytes of data.

    --- 2.2.2.2 ping statistics ---
    5 packets transmitted, 0 received, 100% packet loss, time 14005ms
    cisco@server:~$ Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/projects/unicon/src/unicon/bases/linux/services.py", line 72, in __call__
        self.call_service(*args, **kwargs)
      File "/projects/unicon/src/unicon/plugins/linux/service_implementation.py", line 238, in call_service
        raise SubCommandFailure(self.result, self.match_list)
    unicon.core.errors.SubCommandFailure: ('PING 2.2.2.2 (2.2.2.2) 56(84) bytes of data.\r\n\r\n--- 2.2.2.2 ping statistics ---\r\n5 packets transmitted, 0 received, 100% packet loss, time 14005ms', ['100% packet loss'])
    >>> 


Example with empty error pattern to avoid exception.

.. code-block:: python

    >>> r = l.ping("2.2.2.2", error_pattern=[])
    ping -A -c5 2.2.2.2
    PING 2.2.2.2 (2.2.2.2) 56(84) bytes of data.

    --- 2.2.2.2 ping statistics ---
    5 packets transmitted, 0 received, 100% packet loss, time 14005ms
    cisco@server:~$ 


Example with custom error pattern to trigger exception.

.. code-block:: python

    >>> r = l.ping('127.0.0.1', error_pattern=[' 0% packet loss'])
    ping -A -c5 127.0.0.1
    PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
    64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.018 ms
    64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.022 ms
    64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.022 ms
    64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.024 ms
    64 bytes from 127.0.0.1: icmp_seq=5 ttl=64 time=0.029 ms

    --- 127.0.0.1 ping statistics ---
    5 packets transmitted, 5 received, 0% packet loss, time 801ms
    rtt min/avg/max/mdev = 0.018/0.023/0.029/0.003 ms, ipg/ewma 200.425/0.020 ms
    cisco@server:~$ Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/projects/unicon/src/unicon/bases/linux/services.py", line 72, in __call__
        self.call_service(*args, **kwargs)
      File "/projects/unicon/src/unicon/plugins/linux/service_implementation.py", line 238, in call_service
        raise SubCommandFailure(self.result, self.match_list)
    unicon.core.errors.SubCommandFailure: ('PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.\r\n64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.018 ms\r\n64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.022 ms\r\n64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.022 ms\r\n64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.024 ms\r\n64 bytes from 127.0.0.1: icmp_seq=5 ttl=64 time=0.029 ms\r\n\r\n--- 127.0.0.1 ping statistics ---\r\n5 packets transmitted, 5 received, 0% packet loss, time 801ms\r\nrtt min/avg/max/mdev = 0.018/0.023/0.029/0.003 ms, ipg/ewma 200.425/0.020 ms', [' 0% packet loss'])
    >>> 


.. _linux_sudo:

sudo
----

This service is used to execute commands using ``sudo`` on the device. This can be
used to get a root shell by using `device.sudo()`, as `sudo bash` is the default
command.

===============   ======================    ============================================
Argument          Type                      Description
===============   ======================    ============================================
command           str                       command to execute with sudo (default: bash)
timeout           int (default 60 sec)      timeout value for the overall interaction.
reply             Dialog                    additional dialog
prompt_recovery   bool (default False)      Enable/Disable prompt recovery feature
===============   ======================    ============================================

The sudo password can be specified in the testbed file under the `sudo` credentials.

.. code-block:: yaml

      lnx:
        os: linux
        credentials:
          default:
            username: cisco
            password: cisco
          sudo:
            password: sudo_password


Example with device.sudo().

.. code-block:: python

      In [3]: dev.sudo()

      2021-08-04 14:36:53,472: %UNICON-INFO: +++ lnx with alias 'cli': executing command 'sudo bash' +++
      sudo bash
      [sudo] password for cisco: 
      Linux# 
      Out[3]: '[sudo] password for cisco: '

      In [4]: 


Example with sudo command argument.

.. code-block:: python

      In [5]: dev.sudo('ls')

      2021-08-04 14:37:58,397: %UNICON-INFO: +++ lnx with alias 'cli': executing command 'sudo ls' +++
      sudo ls
      /tmp
      /var
      /opt
      Linux$ 
      Out[5]: '/tmp\r\n/var\r\n/opt'

      In [6]: 
