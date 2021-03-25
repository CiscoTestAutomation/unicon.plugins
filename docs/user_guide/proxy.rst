Connection Through Proxies
==========================

There are several ways to connect to a device via a 'proxied' connection, i.e.
connecting to a device through another system. Unicon supports CLI proxy and
SSH tunnel features. CLI proxy allows a device to connect via another
(Unicon supported) device, SSH tunnel uses the SSH client to create TCP
tunnels to connect to another device via a SSH connection.

.. _unicon_cli_proxy:

CLI Proxy
---------

The CLI proxy works by connecting via one or more proxy devices and executing
a command to start the connection to the next device. The command can be
specified explicitly as part of the proxy definition or it can be determined
based on the connection details (i.e. `protocol`, `ip` and `port` or `command`).

Multiple intermediate devices are supported, you can specify as many proxy
hosts and commands as needed to connect to the target device. Proxy devices
must be defined as a device in the topology file including the relevant
connection details and credentials. Device connection details are used for the
first proxy device only, connection details of intermediate devices are ignored,
you need to explicitly specify a command to connect to an intermediate device.

When the **CLI proxy** feature is when used as part of pyATS the proxy needs to be
specified in the topology YAML file.

.. note::

  If the proxy device has more than one connection defined, you must
  specify the 'via' settings under the connection defaults of the proxy device.


CLI proxy with pyATS topology integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example topology file with a ``proxy`` configuration for the ``cli`` connection.
Please note that credentials have been left out of this example.

.. code:: yaml

    devices:
      jumphost:
        os: linux
        type: linux
        connections:
          cli:
            protocol: ssh
            ip: 127.0.0.1
            port: 2222
      Router:
        os: ios
        type: router
        connections:
          defaults:
            class: unicon.Unicon
          cli:
            protocol: telnet
            ip: 127.0.0.1
            port: 64001
            proxy: jumphost


Connection log (abbreviated) for above example:

.. code::

        %UNICON-INFO: ssh 127.0.0.1 -p 2222
        Last login: Wed Jan 24 08:02:24 2018 from 10.0.2.2
        admin@host:~$ 
        %UNICON-INFO: +++ initializing handle +++
        stty cols 200
        admin@host:~$ stty rows 200
        admin@host:~$ 
        %UNICON-INFO: +++ connection to spawn_command: ssh 127.0.0.1 -p 2222, id: 4394786888 +++
        telnet 127.0.0.1 64001
        Trying 127.0.0.1...
        Connected to 127.0.0.1.
        Escape character is '^]'.

        Router#
        %UNICON-INFO: +++ initializing handle +++

In the above log, you can see the command ``telnet 127.0.0.1 64001`` is
executed to connect to the target device. This command is derived
automatically from the connection details of the target device.

.. note::

    There is no support for *hierarchical* proxy configurations. If you need
    to pass multiple devices to get to the target device, you need to specify
    a list of proxy devices for that device. If a proxy device has a proxy
    specified for its connection, it is ignored.


CLI Proxy topology schema
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: yaml

    devices:

      <name>:
        connections:

          # proxy device only, command is derived from connection details
          <name>:
            proxy: <name> # proxy device name

          # proxy with specific command
          <name>:
            proxy:
              device: <name> # proxy device name
              command: <cmd> # command to connect to target device

          # proxy with lists of commands
          <name>:
            proxy:
              - device: <name> # proxy device name
                command: [ <cmd>, <cmd> ] # list of commands, 
                                          # the last command connects 
                                          # to the next proxy device
              - device: <name> # list of commands using different syntax
                command:
                  - <cmd>
                  - <cmd>

          # multiple proxy devices, last device without specific command
          # derives the command from the connection details
          <name>:
            proxy:
              - device: <name> # proxy device name
                command:
                  - <cmd> # command to connect to next proxy device
              - device: <name>

          # multiple proxy devices with a list of commands for one of the hosts
          <name>:
            proxy: 
              - device: <name> # proxy device name
                command:
                  - <cmd>
                  - <cmd>
              - device: <name> # proxy device name
                command: <cmd>



CLI proxy with Unicon standalone Connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The *CLI Proxy* feature can also be used when using Unicon in standalone mode.
Proxy connections can be specified via the `proxy_connections` argument of the
Connection class.

The `proxy_connections` argument expects a list of ``Connection`` objects with the
start parameter containing the command to be executed to connect to the
next device. If multiple commands should be executed, a list of lists should be
passed, e.g. ``start=[['cmd1','cmd2','cmd3']]``

Below example shows a single proxy connection used to reach the IOS router `R01`.

.. code:: python

        proxy_conn = Connection(hostname='lnx2',
                       start=['ssh -p 2222 localhost'],
                       os='linux',
                       credentials={'default': {'username': 'admin', 'password': 'cisco'}})

        c = Connection(hostname='R01',
                       start=['telnet 10.3.3.1'],
                       os='ios',
                       credentials={'default': {'username': 'admin', 'password': 'cisco'}},
                       proxy_connections=[proxy_conn])
        c.connect()



CLI Proxy examples
~~~~~~~~~~~~~~~~~~

**Connecting to ConfD/NSO CLI via a linux server**

.. code:: yaml

    devices:
      lnx:
        os: linux
        type: linux
        credentials:
            default:
                username: cisco
                password: cisco
        connections:
          defaults:
            class: unicon.Unicon
          cli:
            protocol: ssh
            ip: 127.0.0.1
            port: 2222
      nso:
        os: confd
        type: nso
        credentials:
            default:
                username: admin
                password: admin
        connections:
          defaults:
            class: unicon.Unicon
          cli:
            command: ncs_cli -u admin -C
            proxy: lnx

.. code:: python

      from pyats.topology import loader
      tb = loader.load('nso.yaml')

      # Connect to target device, proxy connection is done automatically
      n = tb.devices.nso
      n.connect(via='cli')


**Connecting to a VNF console via Cloud Services Platform (CSP)**

.. code:: yaml

    # Example with IOS VNF on CSP

    devices:
        Router:
            type: router
            os: ios
            credentials:
                default:
                    username: cisco
                    password: cisco
            connections:
                defaults:
                    class: unicon.Unicon
                cli:
                    command: telnet 7005
                    proxy: csp
        csp:
            type: nfvi
            os: confd
            platform: csp
            credentials:
                default:
                    username: admin
                    password: admin
            connections:
                defaults:
                    class: unicon.Unicon
                cli:
                    protocol: ssh
                    ip: 172.27.132.75

.. code:: python

      from pyats.topology import loader
      tb = loader.load('csp.yaml')

      # Connect to target device, proxy connection is done automatically
      r = tb.devices.Router
      r.connect(via='cli')


**Connecting via multiple proxy devices**

Topology file with target device `Sw03` and three intermediate devices, `lnx`, `R01` and `R02`.

.. code:: yaml

      testbed:
          credentials:
              default:
                  username: cisco
                  password: cisco
      devices:
          lnx:
            type: linux
            os: linux
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                protocol: ssh
                ip: 127.0.0.1
                port: 2222

          R01:
            os: ios
            type: router
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                protocol: telnet
                ip: 127.0.0.1
                port: 64001

          R02:
            os: ios
            type: router
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                protocol: telnet
                ip: 127.0.0.1
                port: 64002

          Sw03:
            os: ios
            type: switch
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                protocol: telnet
                ip: 10.2.3.3
                proxy:
                  - device: lnx
                    command: telnet 10.3.3.1  # Command specifies how to connect to R01
                  - device: R01
                    command: telnet 2.2.2.2   # Command specifies how to connect to R02
                  - device: R02  # no command, use the connection details of Sw03


Example script and abbreviated connection log.

.. code:: python

    >>> 
    >>> from pyats.topology import loader
    >>> tb = loader.load('cliproxy.yaml')
    >>> sw = tb.devices['Sw03']
    >>> sw.connect())

    2018-02-13T12:20:53: %UNICON-INFO: +++ initializing context +++

    ...

    2018-02-13T12:20:53: %UNICON-INFO: connection via proxy lnx

    2018-02-13T12:20:53: %UNICON-INFO: connection to lnx

    Linux$ 
    2018-02-13T12:20:53: %UNICON-INFO: +++ initializing handle +++

    2018-02-13T12:20:53: %UNICON-INFO: connection via proxy R01

    2018-02-13T12:20:53: %UNICON-INFO: connection to R01
    telnet 10.3.3.1
    Trying 10.3.3.1...
    Connected to 10.3.3.1.
    Escape character is '^]'.


    User Access Verification
     
    Password:
    R01>
    2018-02-13T12:20:53: %UNICON-INFO: +++ initializing handle +++
    enable
    Password:
    R01#
    2018-02-13T12:20:53: %UNICON-INFO: connection via proxy R02

    2018-02-13T12:20:53: %UNICON-INFO: connection to R02
    telnet 2.2.2.2
    Trying 2.2.2.2...
    Connected to 2.2.2.2.
    Escape character is '^]'.


    User Access Verification
     
    Password:
    R02>
    2018-02-13T12:20:53: %UNICON-INFO: +++ initializing handle +++
    enable
    Password:
    R02#
    2018-02-13T12:20:53: %UNICON-INFO: connection to Sw03
    telnet 10.2.3.3
    Trying 10.2.3.3 ... Open

    User Access Verification
     
    Password:
    Sw03>


**CLI proxy with standalone Unicon Connections**

Below example code and abbreviated execution log shows how to instantiate the
Connection objects to create a proxied connection.

.. code:: python

      >>> from unicon import Connection
      >>> 
      >>> proxy_conn = Connection(hostname='lnx2',
      ...                start=['ssh lnx2'],
      ...                os='linux',
      ...                credentials={'default': {'username': 'admin', 'password': 'cisco'}})

      >>> 
      >>> c = Connection(hostname='R01',
      ...                start=['telnet 10.3.3.1'],
      ...                os='ios',
      ...                credentials={'default': {'username': 'admin', 'password': 'cisco'}})
      ...                proxy_connections=[proxy_conn])

      >>> c.connect()

      2018-02-13T12:56:30: %UNICON-INFO: connection via proxy lnx2

      2018-02-13T12:56:30: %UNICON-INFO: connection to lnx2

      Linux$ 
      2018-02-13T12:56:31: %UNICON-INFO: +++ initializing handle +++

      2018-02-13T12:56:31: %UNICON-INFO: connection to R01
      telnet 10.3.3.1
      Trying 10.3.3.1...
      Connected to 10.3.3.1.
      Escape character is '^]'.


      User Access Verification
       
      Password:
      R01>
      2018-02-13T12:56:31: %UNICON-INFO: +++ initializing handle +++


**CLI proxy with Dual RP device**

Below example code shows how to use CLI proxy for dual rp device.

.. code:: yaml

    # Example with IOSXE Ha device - testbed.yaml

    devices:
      Router:
        alias: uut
        os: iosxe
        credentials:
          default:
            password: cisco
            username: cisco
          enable:
            password: cisco
        connections:
          defaults:
            class: unicon.Unicon
          a:
            protocol: telnet
            ip: 1.1.1.1
            port: 2001
            proxy: jump_host
          b:
            protocol: telnet
            ip: 172.27.114.25
            port: 2002
            proxy: jump_host

      jump_host:
        alias: jh
        connections:
          cli:
            ip: 2.2.2.2
            port: 22
            protocol: ssh
        credentials:
          default:
            password: pyats
            username: virl
        os: linux
        type: linux

.. code:: python

      >>> # pyats shell --testbed-file testbed.yaml
      >>> from genie.testbed import load
      >>> testbed = load('testbed.yaml')
      -------------------------------------------------------------------------------            
      >>> d = testbed.devices['uut']
      >>> d.connect()

      2020-08-14 14:08:15,959: %UNICON-INFO: +++ Router logfile /tmp/Router-cli-20200814T140815956.log +++

      2020-08-14 14:08:15,960: %UNICON-INFO: +++ Unicon plugin iosxe +++

      2020-08-14 14:08:15,995: %UNICON-INFO: +++ Router logfile /tmp/Router-cli-20200814T140815956.log +++

      2020-08-14 14:08:15,996: %UNICON-INFO: +++ Unicon plugin iosxe +++

      2020-08-14 14:08:16,033: %UNICON-INFO: +++ Router logfile /tmp/Router-cli-20200814T140815956.log +++

      2020-08-14 14:08:16,036: %UNICON-INFO: +++ Unicon plugin iosxe +++

      2020-08-14 14:08:16,039: %UNICON-INFO: connection via proxy jump_host

      2020-08-14 14:08:16,053: %UNICON-INFO: +++ connection to spawn: ssh -l virl 2.2.2.2 -p 22, id: 139774725172192 +++

      2020-08-14 14:08:16,054: %UNICON-INFO: connection to jump_host
      virl@2.2.2.2's password: 
      Welcome to Ubuntu 16.04.5 LTS (GNU/Linux 4.4.0-139-generic x86_64)

      Last login: Fri Aug 14 18:06:18 2020 from 10.0.10.1
      virl@cisco.com:~$ 

      2020-08-14 14:08:19,351: %UNICON-INFO: +++ initializing handle +++


      2020-08-14 14:08:19,351: %UNICON-INFO: connection via proxy jump_host

      2020-08-14 14:08:19,362: %UNICON-INFO: +++ connection to spawn: ssh -l virl 2.2.2.2 -p 22, id: 139774725151152 +++

      2020-08-14 14:08:19,363: %UNICON-INFO: connection to jump_host
      virl@2.2.2.2's password: 
      Welcome to Ubuntu 16.04.5 LTS (GNU/Linux 4.4.0-139-generic x86_64)

      Last login: Fri Aug 14 18:08:19 2020 from 10.0.10.1
      virl@cisco.com:~$ 

      2020-08-14 14:08:22,638: %UNICON-INFO: +++ initializing handle +++

      2020-08-14 14:08:22,640: %UNICON-INFO: +++ connection to spawn: ssh -l virl 2.2.2.2 -p 22, id: 139774725172192 +++

      2020-08-14 14:08:22,641: %UNICON-INFO: +++ connection to spawn: ssh -l virl 2.2.2.2 -p 22, id: 139774725151152 +++
      telnet 1.1.1.1 2001
      Trying 1.1.1.1...
      Connected to 1.1.1.1.
      Escape character is '^]'.

      Router-stby#
      Router-stby#

      telnet 1.1.1.1 2002
      Trying 1.1.1.1...
      Connected to 1.1.1.1.
      Escape character is '^]'.

      Router#
      Router#
      Router-stby#
      >>> 


.. _unicon_ssh_tunnel:

SSH Tunnel
----------

The SSH tunnel feature uses the escape sequence feature of the `ssh` command
line client to create TCP tunnel connections via a (linux) server. This server
acts as a 'jumphost' or proxy device to connect to devices that are
reachable only through this server and not directly.

Connections via the SSH tunnel feature make a TCP connection to the device via
the SSH connection.

The current implementation supports connections from the SSH client host (i.e.
where the pyATS script runs) to devices behind the (linux) server in the lab.

You can find more information on the escape sequence of the OpenSSH client here:
|ssh_link|.

.. |ssh_link| raw:: html

   <a href="https://www.freebsd.org/cgi/man.cgi?query=ssh&sektion=1#ESCAPE_CHARACTERS" target="_blank">SSH escape characters</a>


To configure a connection to use the SSH tunnel feature, configure ``sshtunnel`` key under
the connection and add the ``host`` key with the device name or server name as the value.

The SSH tunnel host can be a testbed server or can be another device from the testbed.



SSH tunnel with pyATS topology integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example topology file with a ``sshtunnel`` configuration for the ``a`` connection of device R2.

.. code:: yaml

        testbed:
          servers:
            js:
              address: 127.0.0.1
              credentials:
                  ssh:
                      username: cisco
                      password: cisco
              custom:
                port: 2222
                ssh_options: -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null

        devices:
            R2:
              os: ios
              type: router
              credentials:
                default:
                  username: cisco
                  password: cisco
              connections:
                defaults:
                  class: unicon.Unicon
                a:
                  protocol: ssh
                  ip: 10.0.0.1
                  port: 22
                  sshtunnel:
                      host: js


Example script and abbreviated connection log.

.. code:: python

    >>> 
    >>> from pyats.topology import loader
    >>> tb = loader.load('sshtunnel.yaml')
    >>> r2 = tb.devices['R2']
    >>> r2.connect())
    2018-03-29T18:19:26: %UNICON-INFO: Connecting proxy host js

    2018-03-29T18:19:26: %UNICON-INFO: connection to js

    2018-03-29T18:19:26: %UNICON-INFO: +++ connection to spawn_command: ssh -l cisco -p 2222 127.0.0.1 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null, id: 4440916152 +++

    2018-03-29T18:19:26: %UNICON-INFO: ssh -l cisco -p 2222 127.0.0.1 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
    Warning: Permanently added '[127.0.0.1]:2222' (RSA) to the list of known hosts.
    Password:

    Linux$ 
    2018-03-29T18:19:26: %UNICON-INFO: +++ initializing handle +++
    stty cols 200
    Linux$ stty rows 200
    Linux$ 
    2018-03-29T18:19:26: %UNICON-INFO: Attaching  all Subcommands
    2018-03-29T18:19:26: %UNICON-INFO: Adding tunnel 127.0.0.1:20001 for 10.0.0.1:22
    2018-03-29T18:19:26: %UNICON-INFO: Device 'R2' connection 'a' via new SSH tunnel 127.0.0.1:20001

    2018-03-29T18:19:26: %UNICON-INFO: connection to R2

    2018-03-29T18:19:26: %UNICON-INFO: +++ connection to spawn_command: ssh -l cisco 127.0.0.1 -p 20001 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null, id: 4442821240 +++

    2018-03-29T18:19:26: %UNICON-INFO: ssh -l cisco 127.0.0.1 -p 20001 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
    Warning: Permanently added '[127.0.0.1]:20001' (RSA) to the list of known hosts.
    Password:
    Username: cisco
    Password: cisco
    R2>
    2018-03-29T18:19:26: %UNICON-INFO: +++ initializing handle +++
    enable
    Password: cisco
    R2#
    2018-03-29T18:19:26: %UNICON-INFO: +++ execute  +++
    term length 0
    R2#
    2018-03-29T18:19:26: %UNICON-INFO: +++ execute  +++
    term width 0
    R2#


**SSH tunnel with IPv6 target device**

Below example topology file shows a router device that is reachable via IPv6 via the IPv4 jump host.

Unicon will create a SSH connection to the jump host and create the IPv4 tunnel that connects to the IPv6 target device from the jump host.

.. code:: yaml

          devices:
              js:
                os: linux
                type: server
                credentials:
                  default:
                    username: cisco
                    password: cisco
                connections:
                  defaults:
                    class: unicon.Unicon
                  ssh:
                    protocol: ssh
                    ip: 10.0.0.1
                    port: 22
                    ssh_options: -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null

              R1:
                os: ios
                type: router
                credentials:
                  default:
                    username: cisco
                    password: cisco
                connections:
                  defaults:
                    class: unicon.Unicon
                  vty:
                    protocol: ssh
                    ip: 2001:abcd::1
                    sshtunnel:
                        host: js



SSH Tunnel topology schema
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: YAML

    devices:

      <name>:
        connections:

          <name>:
            sshtunnel:
              # tunnel device name is required
              host: <device name>
              # optional settings
              tunnel_ip: <ip> # default: 127.0.0.1
              tunnel_port: <port> # default: automatic from port 20000 and up


SSH Tunnel with standalone Unicon Connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below example code shows how to instantiate the
Connection objects to create a tunneled connection.

.. code:: python

      from unicon import Connection

      proxy = Connection(hostname='linux',
                     start=['ssh jumphost'],
                     os='linux',
                     credentials={'default': {'username': 'cisco', 'password': 'cisco'}})
      proxy.connect()

      from unicon.sshutil import sshtunnel

      tunnel_port = sshtunnel.add_tunnel(
                  proxy_conn=proxy,
                  target_address='1.1.1.1',
                  target_port=23
                  )

      c = Connection(hostname='R1',
                     start=['telnet 127.0.0.1 {}'.format(tunnel_port)],
                     os='ios',
                     credentials={'default': {'username': 'cisco', 'password': 'cisco'}})
      c.connect()



Limitations
-----------

- UDP tunnels are currently not supported.



.. sectionauthor:: Dave Wapstra <dwapstra@cisco.com>

