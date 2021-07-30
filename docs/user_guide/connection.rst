Connection Basics
=================

.. _unicon_connection:


There are two primary ways of creating device CLI connections using Unicon:

1. using pyATS testbed YAML files
2. using native Python Unicon APIs


Using pyATS Testbed YAML
------------------------

The simplest way to create a device connection using Unicon is through a 
pyATS testbed YAML file. 

The testbed YAML file contains all necessary information that instructs Unicon
on *how* a connection should be established (eg, using what parameters and 
credentials). 

.. code-block:: yaml

    # Example
    # -------
    #
    #   a simple pyATS testbed YAML file

      
  devices:
      csr1000v-1:
          type: router
          os: iosxe
          credentials:
              default:
                  password: cisco123
                  username: admin
              enable:
                  password: cisco123
          connections:
              cli:
                  protocol: ssh
                  ip: 168.10.1.35
 
Note that in the above file, the following key values are used by Unicon
to identify the proper plugin to use to create the underlying connection:

  * ``os:`` -  OS details of the device [required]
  * ``platform:`` -  platform of the the device [optional]
  * ``model:`` - platform model of the device [optional]

If an equivalent unicon connection plugin is not found for a device, unicon
will use the ``generic plugin``. 

.. tip::

    The supported OS and platform information can be found here: `Supported Platforms`_.


.. _Supported Platforms: introduction.html#supported-platforms

Now, you can establish connectivity to this device within your
test scripts, or within Python:

.. code-block:: python

    # Example
    # -------
    #
    #   using the above testbed yaml file in pyATS

    from pyats.topology import loader

    testbed = loader.load('my-testbed.yaml')

    device = testbed.devices['csr1000v-1']
    
    device.connect()

    device.execute('show version')

Customizing Your Connection
"""""""""""""""""""""""""""

In order to allow users to tune unicon plugin behavior without the need for
any code changes, several kinds of overrides may be made from the testbed
YAML itself.

Connecting to a pyATS device via unicon ultimately results in a unicon
:ref:`Connection<unicon_connection>` object being created.

The following parameters are eligible for override under the ``arguments`` key
in the testbed YAML connection block:

- ``learn_hostname``
- ``prompt_recovery``
- ``init_exec_commands``
- ``init_config_commands``
- ``mit``
- ``log_stdout``
- ``debug``
- ``goto_enable``
- ``standby_goto_enable``


.. _settings_control:

A connection, once created, has a ``settings`` parameter whose contents and
defaults are plugin-dependent.  It is possible to override these settings
from the testbed YAML file via the ``settings`` key.

Settings can be accessed :ref:`here<controlled_settings>`.

A connection is assigned a plugin-dependent list of services when it is created.
It is possible to override any service attribute from the testbed YAML file
via the ``service_attributes`` key.


The following testbed YAML shows these three kinds of override:

.. code-block:: yaml

  device1:
      os: 'nxos'
      platform: 'n7k'
      type: 'router'
      credentials:
          default:
              username: lab
              password: lab
      connections:
        a:
          protocol: telnet
          ip: 10.64.70.11
          port: 2042

          arguments:
            connection_timeout: 120
            mit: True

          settings:
            ESCAPE_CHAR_CHATTY_TERM_WAIT: 1

          service_attributes:
            ping:
              timeout: 1234


.. note ::

   Details specified under the ``arguments``, ``settings`` or
   ``service_attributes`` connection block keys take
   precedence over any identically-named details passed to the
   ``device.connect()`` call.

   Using the above testbed YAML as an example:

   Calling ``device1.connect(connection_timeout=240)``
   results in ``device1.connection_timeout`` being set to 120.

   Calling
   ``device1.connect(settings=dict(ESCAPE_CHAR_CHATTY_TERM_WAIT=10))``
   results in ``device1.settings.ESCAPE_CHAR_CHATTY_TERM_WAIT`` being set to 1.

   Calling ``device1.connect(service_attributes=dict(ping=dict(timeout=1)))``
   results in ``device1.ping.timeout`` being set to 1234.


If you want to change to default timeout value for execute and configure service,
you can set the ``EXEC_TIMEOUT`` and ``CONFIG_TIMEOUT`` in the testbed file:

.. code-block:: yaml

  device1:
      os: 'nxos'
      platform: 'n7k'
      type: 'router'
      credentials:
          default:
              username: lab
              password: lab
      connections:
        a:
          protocol: telnet
          ip: 10.64.70.11
          port: 2042

          settings:
            EXEC_TIMEOUT: 120
            CONFIG_TIMEOUT: 120


Example: Single NXOS
""""""""""""""""""""

Every other platform can use the same sample file by changing the os, platform, model. The Moonshine platform does not require a username or password, so
these are omitted (see below for an example).

.. code-block:: yaml

  step-n7k-1:
      os: 'nxos'
      platform: 'n7k'
      type: 'router'
      credentials:
          default:
              username: lab
              password: lab
      connections:
        defaults:
          class: 'unicon.Unicon'
        a:
          protocol: telnet
          ip: 10.64.70.11
          port: 2042

For more info on testbed refer to :ref:`topology<schema>` package.


**Connecting to the device using the above testbed file:**

.. note::

  unicon Connection arguments may be passed in the pyATS
  ``device.connect()``.  For example: ``device.connect(learn_hostname=True)``.



.. code-block:: python

  >>> from pyats.topology import loader
  >>> tb = loader.load("testbed.yaml")
  >>> uut = tb.devices['step-n7k-1']
  >>> uut.connect()

  2016-04-06T12:06:50: %UNICON-INFO: +++ initializing context +++

  2016-04-06T12:06:50: %UNICON-INFO: +++ initializing state_machine +++

  2016-04-06T12:06:50: %UNICON-INFO: +++ initializing services +++

  2016-04-06T12:06:50: %UNICON-INFO: adding service  ping   :  <unicon.plugins.generic.service_implementation.Ping object at 0x10441ff98>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  reload   :  <unicon.plugins.nxos.service_implementation.Reload object at 0x10441fef0>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  sendline   :  <unicon.plugins.generic.service_implementation.Sendline object at 0x10441ffd0>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  list_vdc   :  <unicon.plugins.nxos.service_implementation.ListVdc object at 0x10441f978>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  copy   :  <unicon.plugins.generic.service_implementation.Copy object at 0x10443b048>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  switchto   :  <unicon.plugins.nxos.service_implementation.SwitchVdc object at 0x10443b0b8>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  disable   :  <unicon.plugins.generic.service_implementation.Disable object at 0x10443b0f0>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  send   :  <unicon.plugins.generic.service_implementation.Send object at 0x10443b128>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  delete_vdc   :  <unicon.plugins.nxos.service_implementation.DeleteVdc object at 0x10443b160>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  ping6   :  <unicon.plugins.nxos.service_implementation.Ping6 object at 0x10443b198>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  execute   :  <unicon.plugins.generic.service_implementation.Execute object at 0x10443b208>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  enable   :  <unicon.plugins.generic.service_implementation.Enable object at 0x10443b240>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  shellexec   :  <unicon.plugins.nxos.service_implementation.ShellExec object at 0x10443b278>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  switchback   :  <unicon.plugins.nxos.service_implementation.SwitchbackVdc object at 0x10443b2b0>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  config   :  <unicon.plugins.generic.service_implementation.Config object at 0x10443b2e8>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  create_vdc   :  <unicon.plugins.nxos.service_implementation.CreateVdc object at 0x10443b320>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  expect   :  <unicon.plugins.generic.service_implementation.Expect object at 0x10443b358>

  2016-04-06T12:06:50: %UNICON-INFO: adding service  log_user   :  <unicon.plugins.generic.service_implementation.LogUser object at 0x10443b390>

  2016-04-06T12:06:50: %UNICON-INFO: connection to step-n7k-1

  2016-04-06T12:06:50: %UNICON-INFO: +++ connection to spawn_command: telnet 10.64.70.24 2061, id: 4358177400 +++

  2016-04-06T12:06:50: %UNICON-INFO: telnet 10.64.70.24 2061
  Trying 10.64.70.24...
  Connected to ts-nostg-mm18.cisco.com.
  Escape character is '^]'.

  step-n7k-1#
  2016-04-06T12:06:51: %UNICON-INFO: +++ initializing handle +++

  2016-04-06T12:06:51: %UNICON-INFO: +++ execute  +++
  term length 0
  step-n7k-1#
  2016-04-06T12:06:51: %UNICON-INFO: +++ execute  +++
  term width 511
  step-n7k-1#
  2016-04-06T12:06:51: %UNICON-INFO: +++ execute  +++
  terminal session-timeout 0
  step-n7k-1#
  2016-04-06T12:06:51: %UNICON-INFO: +++ config  +++
  config term
  Enter configuration commands, one per line.  End with CNTL/Z.
  step-n7k-1(config)# no logging console
  step-n7k-1(config)# line console
  step-n7k-1(config-console)# exec-timeout 0
  step-n7k-1(config-console)# terminal width 511
  step-n7k-1(config-console)# end
  step-n7k-1#


Example: Linux Server
"""""""""""""""""""""

Specifying linux device in testbed file template is almost the same as router template, except Unicon
looks for `linux` block in the device details and os has to be mentioned as `linux`

.. code-block:: yaml

  mohamoha-ads:
      os: 'linux'
      credentials:
          default:
              username: admin
              password: password
      connections:
        defaults:
          class: 'unicon.Unicon'
        linux:
          protocol: ssh
          ip: mohamoha-ads
      type: 'linux'


**Connecting to linux machine using above testbed file:**

.. code-block:: python

    >>> from pyats.topology import loader
    >>> tb = loader.load("testbed.yaml")

    >>> server = tb.devices['mohamoha-ads']

    >>> server.connect()

    2016-04-06T12:10:49: %UNICON-INFO: +++ initializing context +++

    2016-04-06T12:10:49: %UNICON-INFO: +++ initializing state_machine +++

    2016-04-06T12:10:49: %UNICON-INFO: +++ initializing services +++

    2016-04-06T12:10:49: %UNICON-INFO: adding service  send   :  <unicon.plugins.generic.service_implementation.Send object at 0x10443b9b0>

    2016-04-06T12:10:49: %UNICON-INFO: adding service  execute   :  <unicon.plugins.linux.service_implementation.Execute object at 0x10443be48>

    2016-04-06T12:10:49: %UNICON-INFO: adding service  sendline   :  <unicon.plugins.generic.service_implementation.Sendline object at 0x10443be80>

    2016-04-06T12:10:49: %UNICON-INFO: adding service  expect   :  <unicon.plugins.generic.service_implementation.Expect object at 0x10443beb8>

    2016-04-06T12:10:49: %UNICON-INFO: adding service  log_user   :  <unicon.plugins.generic.service_implementation.LogUser object at 0x10443bef0>

    2016-04-06T12:10:49: %UNICON-INFO: connection to mohamoha-ads

    2016-04-06T12:10:49: %UNICON-INFO: +++ connection to spawn_command: ssh -l mohamoha 64.103.223.250, id: 4366516064 +++

    2016-04-06T12:10:49: %UNICON-INFO: ssh -l mohamoha 64.103.223.250

    Last login: Mon Apr  4 16:12:21 2016 from 10.232.8.212
    Cisco Linux 5.50-5Server Kickstarted on: Sat Jun 13 05:53:15 PDT 2009.

    bgl-ads-842:129>
    2016-04-06T12:10:49: %UNICON-INFO: +++ initializing handle +++

    2016-04-06T12:10:49: %UNICON-INFO: Attaching  all Subcommands

**Connection to Linux with additional SSH options:**

If you want the linux connection to take additional ssh options, then it's better
to use `command` key. Unicon will take the value of `command` and spawns.
Command value should be the complete command to be spawned.

.. code-block:: yaml

  mohamoha-ads:
      os: 'linux'
      credentials:
          default:
              username: admin
              password: password
      connections:
        defaults:
          class: 'unicon.Unicon'
        linux:
          command: 'ssh -l admin 10.1.1.1 -oHostKeyAlgorithms=+ssh-dss'
      type: 'linux'


**Connecting to another TCP port using SSH:**

If you want to connect to another port with SSH, you can use the port option in the testbed file:

.. code-block:: yaml

  lnx-vm:
      os: 'linux'
      credentials:
          default:
              username: admin
              password: password
      connections:
        defaults:
          class: 'unicon.Unicon'
        linux:
          protocol: ssh
          ip: 10.1.1.1
          port: 2200
      type: 'linux'



Example: Moonshine
""""""""""""""""""

.. _unicon user_guide connection moonshine:

Specifying a Moonshine device in the testbed file template is again very similar to the above examples,
except Unicon looks for the `iosxr` os and `moonshine` type and platform, and no username or password is
required.

.. code-block:: yaml

  bringup:
    xrut:
      base_dir: /auto/xrut/xrut-gold
      sim_dir: /path/to/my/xrut/sim/dir
  devices:
    moonshine-1:
      os: iosxr
      platform: moonshine
      type: moonshine
      credentials:
          default:
              username: admin
              password: password
      connections:
        defaults: {class: unicon.XRUTConnect}
        a: {protocol: xrutconnect}

Please note that devices using the xrutconnect protocol should specify the default connection class as
unicon.XRUTConnect.

For information on how to create such a testbed file via the `xrutbringup` command, passing in a logical
testbed file and a clean.yaml file, please see :ref:`dyntopo xrut working examples moonshine` .


Example: NSO
""""""""""""

.. _unicon user_guide connection nso:

To connect to the Network Service Orchestrator CLI via SSH, use the 'nso' OS type and specify the
ssh port under the connection details.

.. code-block:: yaml

    # example testbed.yaml file for NSO CLI
    devices:
      ncs:
        os: nso
        credentials:
          default:
              username: admin
              password: password
        connections:
          defaults:
            class: unicon.Unicon
            via: cli
          con:
            command: ncs_cli -C
          cli:
            credentials:
              nso:
                  username: admin
                  password: cisco1234
            login_creds: nso
            protocol: ssh
            ip: 127.0.0.1
            port: 2024



**Connecting to NSO CLI via SSH using above testbed file:**

As shown in the example below, use the connect() method to initiate the connection,
specify the 'via' option if no default is configured under the connection defaults.

The ncs.conf configuration file section for the SSH service for NSO is shown below.

.. code-block:: xml

    <cli>
      <enabled>true</enabled>
      <style>c</style>

      <!-- Use the builtin SSH server -->
      <ssh>
        <enabled>true</enabled>
        <ip>0.0.0.0</ip>
        <port>2024</port>
      </ssh>


This example uses the 'cli' connection which initiates a SSH session the to default port of the NSO SSH service.

.. code-block:: python

    >>> from pyats.topology import loader
    >>> tb = loader.load("testbed.yaml")

    >>> ncs = tb.devices.ncs

    >>> ncs.connect(via='cli')

    2017-06-02T08:15:55: %UNICON-INFO: +++ initializing context +++

    2017-06-02T08:15:55: %UNICON-INFO: +++ initializing state_machine +++

    2017-06-02T08:15:55: %UNICON-INFO: +++ initializing services +++

    2017-06-02T08:15:55: %UNICON-INFO: adding service  execute   :  <unicon.plugins.nso.service_implementation.Execute object at 0x7ff3549ba630>

    2017-06-02T08:15:55: %UNICON-INFO: adding service  cli_style   :  <unicon.plugins.nso.service_implementation.CliStyle object at 0x7ff3549ba668>

    2017-06-02T08:15:55: %UNICON-INFO: adding service  log_user   :  <unicon.plugins.generic.service_implementation.LogUser object at 0x7ff3549ba6a0>

    2017-06-02T08:15:55: %UNICON-INFO: adding service  sendline   :  <unicon.plugins.generic.service_implementation.Sendline object at 0x7ff3549ba6d8>

    2017-06-02T08:15:55: %UNICON-INFO: adding service  expect   :  <unicon.plugins.generic.service_implementation.Expect object at 0x7ff3549ba710>

    2017-06-02T08:15:55: %UNICON-INFO: adding service  configure   :  <unicon.plugins.nso.service_implementation.Configure object at 0x7ff3549ba748>

    2017-06-02T08:15:55: %UNICON-INFO: adding service  send   :  <unicon.plugins.generic.service_implementation.Send object at 0x7ff3549ba780>

    2017-06-02T08:15:55: %UNICON-INFO: connection to ncs

    2017-06-02T08:15:55: %UNICON-INFO: +++ connection to spawn_command: ssh -l admin 127.0.0.1 -p 2024, id: 140683073268704 +++

    2017-06-02T08:15:55: %UNICON-INFO: ssh -l admin 127.0.0.1 -p 2024
    admin@127.0.0.1's password:

    admin connected from 127.0.0.1 using ssh on nso-dev-server
    admin@ncs# 
    2017-06-02T08:15:55: %UNICON-INFO: +++ initializing handle +++

    2017-06-02T08:15:55: %UNICON-INFO: +++ None  +++
    paginate false
    admin@ncs# 
    2017-06-02T08:15:55: %UNICON-INFO: +++ execute  +++
    screen-length 0
    admin@ncs# 
    2017-06-02T08:15:55: %UNICON-INFO: +++ execute  +++
    screen-width 0
    admin@ncs# 
    2017-06-02T08:15:55: %UNICON-INFO: Attaching  all Subcommands
    >>> 



**Connecting to NSO CLI via ncs_cli command using above testbed file**

It is also possible to run the ncs_cli command to initiate the CLI session, 
use the 'command' option in the testbed.yaml file to specify the ncs_cli command.

Specify the 'via' option if the default is not specified in the connection defaults.


.. code-block:: python

    >>> ncs.connect(via='con')

    2017-06-02T08:19:19: %UNICON-INFO: +++ initializing context +++

    2017-06-02T08:19:19: %UNICON-INFO: +++ initializing state_machine +++

    2017-06-02T08:19:19: %UNICON-INFO: +++ initializing services +++

    2017-06-02T08:19:19: %UNICON-INFO: adding service  send   :  <unicon.plugins.generic.service_implementation.Send object at 0x7fab8e932320>

    2017-06-02T08:19:19: %UNICON-INFO: adding service  log_user   :  <unicon.plugins.generic.service_implementation.LogUser object at 0x7fab8e932358>

    2017-06-02T08:19:19: %UNICON-INFO: adding service  configure   :  <unicon.plugins.nso.service_implementation.Configure object at 0x7fab8e932390>

    2017-06-02T08:19:19: %UNICON-INFO: adding service  cli_style   :  <unicon.plugins.nso.service_implementation.CliStyle object at 0x7fab8e9323c8>

    2017-06-02T08:19:19: %UNICON-INFO: adding service  execute   :  <unicon.plugins.nso.service_implementation.Execute object at 0x7fab8e932400>

    2017-06-02T08:19:19: %UNICON-INFO: adding service  sendline   :  <unicon.plugins.generic.service_implementation.Sendline object at 0x7fab8e932438>

    2017-06-02T08:19:19: %UNICON-INFO: adding service  expect   :  <unicon.plugins.generic.service_implementation.Expect object at 0x7fab8e932470>

    2017-06-02T08:19:19: %UNICON-INFO: connection to ncs

    2017-06-02T08:19:19: %UNICON-INFO: +++ connection to spawn_command: ncs_cli -C, id: 140374808144136 +++

    2017-06-02T08:19:19: %UNICON-INFO: ncs_cli -C

    dwapstra connected from 10.0.2.2 using ssh on nso-dev-server
    dwapstra@ncs# 
    2017-06-02T08:19:19: %UNICON-INFO: +++ initializing handle +++

    2017-06-02T08:19:19: %UNICON-INFO: +++ None  +++
    paginate false
    dwapstra@ncs# 
    2017-06-02T08:19:19: %UNICON-INFO: +++ execute  +++
    screen-length 0
    dwapstra@ncs# 
    2017-06-02T08:19:19: %UNICON-INFO: +++ execute  +++
    screen-width 0
    dwapstra@ncs# 
    2017-06-02T08:19:19: %UNICON-INFO: Attaching  all Subcommands



Example: ConfD
""""""""""""""

.. _unicon user_guide connection confd:

To connect to ConfD based CLI via SSH, use the 'confd' OS type and specify the
ssh port (if needed) under the connection details.

For NSO, the 'os' needs to be specified, 'platform' can be omitted.
For CSP, ESC and NFVIS, the 'platform' needs to be specified.

.. code-block:: yaml

    # example testbed.yaml file for NSO CLI
    devices:
      ncs:
        os: confd
        type: router
        # platform: 'csp', 'esc' or 'nfvis'
        credentials:
          default:
              username: admin
              password: cisco1234
        connections:
          defaults:
            class: unicon.Unicon
            via: cli
          cli:
            protocol: ssh
            ip: 127.0.0.1
            port: 2024



Example: VOS
""""""""""""

.. _unicon user_guide connection vos:

To connect to Cisco Unified Collaboration based CLI via SSH, use the 'vos' OS type and specify the
ssh port (if needed) under the connection details.

.. code-block:: yaml

    # example testbed.yaml file for VOS CLI
    devices:
      cm:
        os: vos
        type: server
        credentials:
          default:
              username: admin
              password: cisco1234
        connections:
          defaults:
            class: unicon.Unicon
            via: cli
          cli:
            protocol: ssh
            ip: 10.0.0.1
            port: 22


pyATS Connection Pool
---------------------
Unicon (IOSXE, NXOS and IOSXR) plugins now support creating a pool of shareable
connections to be distributed among device action requests promoting speed and
avoiding race condition and deadlocks.

.. code-block:: python

    # Example
    # -------
    #
    # Connection pool using unicon.Unicon class example
    # Assuming we have a device that is defined in the testbed yaml file as above

    # using the above device, create a pool of 5 workers
    >>> device.start_pool(alias = 'pool', ----- > Connection pool will be accessed as "device.pool"
                          via = 'mgmt',   ----- > Connection name as in testbed yaml
                          size = 5)

    # Now all action requests sent to the device will run simultaneously on the
    # 5 connections (knows as workers) on a first come first serve basis.

Check here for more details on pyATS `Connection Pool`_ feature.

.. _Connection Pool: https://pubhub.devnetcloud.com/media/pyats/docs/connections/sharing.html#connection-pools



Python APIs
-----------

This section covers how to connect to a device in standalone mode, using raw 
Python APIs directly. 

To connect to a device, you need.
    * IP address
    * Hostname
    * OS
    * Credentials

Please make sure that device is up and booted. In the following
example, we are establishing connection to a *dual rp* NXOS device.

.. code-block:: python

    from unicon import Connection
    dev = Connection(hostname='n7k2-1',
                     start=['telnet 172.27.114.43 2037',
                            'telnet 172.27.114.43 2038'],
                     credentials={'default': {'username': 'admin', 'password': 'Cisc0123'}},
                     os='nxos')
    dev.connect()

Arguments:

    * **hostname**: must be same as the exact hostname of the device.
      Do not append prompt characters like '#' or '$'

    * **os**: The os of the device to connect to.  This selects a unicon plugin.

    * **start**: It must be a list of commands which needs to be invoked for starting a connection.
      Generally it will be of the format `telnet xxx xxx`. But it could take any value.

    * **credentials**: A dictionary of named credentials used to interact with the device.

    * **platform**: The platform of the device to connect to.  This selects a
      unicon sub-plugin under the given plugin identified with the ``os``
      argument.  *(Optional)*

    * **model**: The model of the device to connect to.  This selects a
      unicon sub-sub-plugin under the given plugin identified with the ``os``
      and ``platform`` arguments.  *(Optional)*

    * **connection_timeout**: Connection timeout value to connect the device.
      Default value is ``60 sec``. *(Optional)*

    * **proxy_connections**: Connection object which is use to establish proxy connection.
      Default value is ``None``. *(Optional)*

    * **alias**: Connection alias. Default value is ``None``. *(Optional)*

    * **login_creds**: A single credential name or a list of credentials for
      authenticating against the device.  Default value is ``default``. *(Optional)*

    * **cred_action**: A dictionary with credential names and post password action statement.
      This allows the user to specify e.g. `sendline` to be sent after a credential password.
      The typical use case is a terminal server connection where a return will get a response
      from the device. *(Optional)*

    * **learn_hostname**: Set to `True` if the actual hostname set on the device
      differs from the hostname parameter. *(Optional)*

    * **learn_os**: Set to `True` if the device os is not provided, it will try to
      learn the device os and redirect to the learned plugin. *(Optional)*

    * **prompt_recovery**: Set `True` for using prompt recovery feature. Default value is `False`.
      Click :ref:`prompt_recovery_label` for more information on the feature. *(Optional)*

    * **init_exec_commands**: List of exec commands to use when initializing the connection.
      This option overrules the default settings for the plugin and uses the
      user specified initialization commands. Can also be passed in the
      connection block in the yaml file. *(Optional)*

    * **init_config_commands**: List of config commands to use when initializing the connection.
      This option overrules the default settings for the plugin and uses the user specified initialization commands.
      Config commands will not be executed on the standby RP.
      Config commands are not available on Linux and ISE plugins. Can also be
      passed in the connection block in the yaml file. *(Optional)*

    * **logfile**: Filename to log all device interaction to. By default, a file will
      be created in /tmp based on the hostname, via (if specified) and timestamp. *(Optional)*

    * **log_buffer**: Set to `True` to use a log_buffer instead of a logfile, no logfile will be created.
      The log buffer can be accessed via connection.log_buffer attribute. *(Optional)*

    * **mit**: Boolean option to maintain initial state on connect. The state detected
      on connect() is maintained, no connection initialization is done and the
      exec and config initialization commands are not executed.  It is possible to use
      the `mit` option with HA connections, however please note that HA initialization is not done.
      Default is False. For more info on device state, see :doc:`Statemachine <../developer_guide/statemachine>`
      *(Optional)*

    * **settings**: Dictionary or Settings class instance with updated settings for this connection.
      Pass a dictionary to update some of the settings, or pass a Settings object with all settings.
      *(Optional)*

    * **overwrite_settings**: Boolean option to allow settings to be appended (if the attribute is a list).
      *(Optional)*

    * **log_stdout**: Boolean option to enable/disable logging to standard output. Default is True.
      *(Optional)*

    * **debug**: Boolean option to enable/disable internal debug logging.
      *(Optional)*

    * **service_attributes**: Dictionary whose keys are service names
      and whose values are dictionaries containing key/value pairs to set on the
      named service.
      *(Optional)*

    * **connect_reply**: Dialog object which user wants to be added in the connection dialog.
      *(Optional)*

    * **goto_enable**: Boolean option to enable/disable connection behavior to go to enable state
      after setting up connection. Default is True.
      *(Optional)*

    * **standby_goto_enable**: Boolean option to enable/disable standby connection behavior to go to
      enable state after setting up connection. Default is True.
      *(Optional)*

    * **trim_line**: Boolean option to enable line trimming if the line has additional `\\r\\n` characters.
      *(Optional)*

    * **reconnect**: Boolean option to enable automatic reconnect in case the connection has not been made
      or the connection was lost. Default: True
      *(Optional)*

For *Single RP* connection, `start` will be a list with only one element.

.. note::

    Connecting to many routing and switching platforms usually requires
    the configured hostname to be known in advance.
    However, sometimes the configured hostname on such a device may be
    unknown and may differ from the ``hostname`` parameter.

    When ``learn_hostname=True`` is specified:

      * unicon attempts to learn the hostname of the device
        by examining the device's prompt.

      * If no hostname can be learned, a warning is thrown and the
        learned hostname is set to a generic pattern.

      * If the learned hostname differs from the ``hostname`` parameter,
        ``dev.previous_hostname`` is set to the original hostname and
        ``dev.hostname`` is overwritten with the newly learned hostname.

      * Once set, the ``learn_hostname`` setting can only be changed by
        destroying and recreating the Connection object.

      * The hostname of the device does not contain the characters :
        #, whitespace characters.


.. note::

    Passive hostname learning is enabled by default and will
    give a warning if the device hostname does not match the learned
    hostname. The learned hostname is only used if `learn_hostname=True`.

    A timeout may occur if the prompt pattern uses the hostname,
    the timeout error includes the hostname and a hint to check
    the hostname if a mismatch was detected.


.. note::

    When using the Linux plugin, it is recommended to use ``learn_hostname=True``.
    With the default prompt pattern for the Linux plugin there is a risk of false prompt
    matching if the output contains one of the prompt characters `> # % ~ $` at the end of a line.


**Disconnecting**

To disconnect a session, you can call the `disconnect()` method from a Unicon connection.
This will terminate the subprocess that is handling the device connection. By default,
Unicon waits about 10 seconds after the process is terminated before returning from the method.
This is to prevent connection issues on rapid connect/disconnect sequences.

To change the default timers used when disconnecting, you can change the `GRACEFUL_DISCONNECT_WAIT_SEC` and
`POST_DISCONNECT_WAIT_SEC` settings on the Settings object.

.. code-block:: python

  dev.settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0
  dev.settings.POST_DISCONNECT_WAIT_SEC = 0


.. _unicon_extend_settings_attributes:

Extend Settings Attributes
""""""""""""""""""""""""""

It is possible to extend list settings attributes of the connection like ``ERROR_PATTERN``
and ``CONFIGURE_ERROR_PATTERN`` by using ``overwrite_settings=False`` argument.

.. code-block:: python

    from unicon import Connection
    settings = {'ERROR_PATTERN': ['test', 'error']}
    dev = Connection(hostname='asr1000',
                     start=['telnet 172.27.114.43 2037'],
                     credentials={'default': {'username': 'admin', 'password': 'Cisc0123'}},
                     os='iosxe',
                     settings=settings,
                     overwrite_settings=False)
    dev.connect()
    dev.settings.ERROR_PATTERN
    ['test',
     'error',
     '^%\\s*[Ii]nvalid (command|input)',
     '^%\\s*[Ii]ncomplete (command|input)',
     '^%\\s*[Aa]mbiguous (command|input)']
    
    # this can be done from testbed yaml as well
    # the following is an example testbed
    devices:
      PE1:
        alias: uut
        os: iosxe
        credentials:
          default:
            password: cisco
            username: admin
          enable:
            password: cisco
        connections:
          defaults:
            class: unicon.Unicon
          a:
            protocol: telnet
            ip: 1.1.1.1
            port: 2039
            arguments:
              overwrite_settings: False
            settings:
              EXEC_TIMEOUT: 300
              ERROR_PATTERN:
                - testbed
                - my ERROR


.. _unicon_override_service_attributes:

Overriding Service Attributes
"""""""""""""""""""""""""""""

When a connection is created, various services are attached to it.  The
selected plugin determines the list of supported services.

It is possible to override attributes of one or more services by specifying
the ``service_attributes`` parameter.

.. code-block:: python

    from unicon import Connection
    dev = Connection(hostname='n7k2-1',
                     start=['telnet 172.27.114.43 2037'],
                     credentials={'default': {'username': 'admin', 'password': 'Cisc0123'}},
                     os='nxos',
                     service_attributes=dict(
                        traceroute=dict(timeout=123),
                        ping=dict(timeout=456)))
    dev.connect()
    dev.traceroute.timeout
    123
    dev.ping.timeout
    456


.. _unicon_credentials:

Credentials
-----------

The ``credentials`` connection parameter defines a dictionary of named
credentials.  A credential is a dictionary typically containing both
``username`` and ``password`` keys.

The ``login_creds`` connection parameter defines an optional sequence of
credential names to try.  Each time the device prompts for a username or
password, the current credential is set to the next credential in the sequence
if a current credential has not already been set.
When a password is sent, the current credential is unset.  The one exception
is when entering an administrator's password on a routing device coming up
without configuration, in this case the current credential is reused.
If the sequence has been exhausted and no more credentials are available to
satisfy a username/password prompt, a
`CredentialsExhaustedError<unicon.core.errors.CredentialsExhaustedError>` is
raised.

Credentials are not retried, any username or password failure causes a
`UniconAuthenticationError<unicon.core.errors.UniconAuthenticationError>`
to be raised.

It is possible to specify the password to use for routing devices to enter
enable mode.  This may be done via the ``enable_password`` entry under the
current credential, or via a separate credential called ``enable``.
Please see :ref:`unicon_enable_password_handling` for details.

Passwords specified as a :ref:`secret_strings` are automatically decoded prior
to being sent to the device.

In pyATS Testbed YAML
"""""""""""""""""""""

Credentials may be specified on a per-testbed, per-device or per-connection
basis, as documented in :ref:`topology_credential_password_modeling`.


.. code-block:: python

    from pyats.topology import loader
    tb = loader.load("""
        devices:
            my_device:
                type: router
                credentials:
                    default:
                        username: admin
                        password: Cisc0123
                    alternate:
                        username: alt_username
                        password: alt_password
                    termserv:
                        username: tsuser
                        password: tspw
                    enable:
                        password: enablepw
                connections:
                    defaults: {class: 'unicon.Unicon'}
                    a:
                      protocol: ssh
                      ip: 10.64.70.11
                      port: 2042
                      login_creds: [termserv, default]
                      ssh_options: "-v -i /path/to/identityfile"

    """)
    dev = tb.devices.my_device
    dev.connect()

    # To connect using different credentials than is contained in the
    # testbed YAML ``login_creds`` key:
    dev.destroy()
    dev.connect(login_creds=['termserv', 'alternate'])


In Python
"""""""""

.. code-block:: python

    dev = Connnection(hostname=uut_hostname,
                       start=[uut_start_cmd],
                       credentials={\
                           {'default': {'username': 'admin', 'password': 'Cisc0123'}},\
                           {'enable': {'password': 'enablepw'}},\
                           {'termserv': {'username': 'tsuser', 'password': 'tspw'}},\
                       },
                       login_creds = ['termserv', 'default'],
                     )


Post credential action
""""""""""""""""""""""

In certain cases, e.g. when using a serial console server, an action is needed to get a response
from the device connected to the serial port. There are two ways to configure this action.
The first one is using a setting, the second one is using a post credential action.
The post credential action takes precedence over the setting.

Example credentials for a device.

.. code-block:: yaml

      my_device:
          type: router
          credentials:
              default:
                  username: admin
                  password: Cisc0123
              terminal_server:
                  username: tsuser
                  password: tspw


Setting the credential action via `settings` in python.

.. code-block:: python

    # Name of the credential after which a "sendline()" should be executed
    dev.settings.SENDLINE_AFTER_CRED = 'terminal_server'


Settings can also be specified for the connection in the topology file as shown below.

.. code-block:: yaml

    connections:
      cli:
        settings:
          SENDLINE_AFTER_CRED: terminal_server


The post credential action supports ``send`` and ``sendline``, you can specify a string to be sent,
e.g. `send( )` to send a space or `send(\\x03)` to send Ctrl-C. Quotes should not be specified.

.. code-block:: yaml

    connections:
      cli:
        login_creds: [terminal_server, default]
        arguments:
          cred_action:
            terminal_server:
              post: sendline()



Logging
-------

Every unicon device connection Logger has 3 handlers.

#. Screen Handler: This logs messages on stdout
#. File Handler: This logs messages in file /tmp/<device>-<alias>-<timestamp>.log. This is default log file. To modify the file value, the logfile parameter can be used.
#. pyATS TaskLog Handler: This logs messages in pyats TaskLog file

Change logfile when connecting.

In unicon standalone mode:

.. code-block:: python

    dev = Connection(hostname=uut_hostname,
                       start=[uut_start_cmd],
                       logfile='user-provided-file')

With pyATS:

.. code-block:: python

    dev.connect(logfile='user-provided-file')

Log level of device output and service messages is `INFO`.

To disable unicon device connection logging, we can set logger level above `logging.INFO`.

.. code-block:: python

    import logging
    uut.log.setLevel(logging.WARNING)

To enable debug logs, use below:

.. code-block:: python

    import logging
    uut.log.setLevel(logging.DEBUG)

Debug log now integrates with pyATS testbed yaml file. You can enable it 
by define the `debug: True` in the yaml file:

.. code-block:: python

    devices:
      PE1:
        connections:
          defaults:
            class: 'unicon.Unicon'
            debug: True

To disable logging to standard output, use the `log_stdout` boolean option.

In unicon standalone mode:

.. code-block:: python

    dev = Connection(hostname=uut_hostname,
                       start=[uut_start_cmd],
                       log_stdout=False)

With pyATS:

.. code-block:: python

    dev.connect(log_stdout=False)


Prompt Recovery Usage
---------------------

In unicon, device connection is 2 step process:

#. Create Device `Connection` object
#. Invoke `connect()` on Device `Connection` object.

The `prompt_recovery` is valid for per connect() call.
To use `prompt_recovery` feature user need to specify it per call i.e when connecting next time, user need to set it again as `True`.

Examples:

To use `prompt_recovery` feature in unicon, use it in the following way:

.. code-block:: python

    from unicon import Connection
    device = Connection(hostname='R2', start=['telnet localhost 15000'], prompt_recovery=True)
    device.connect()

If user wishes to enable `prompt_recovery` after creating Device Connection object, it can be done in the following way:

.. code-block:: python

    from unicon import Connection
    device = Connection(hostname='R2', start=['telnet localhost 15000'])
    device.context.prompt_recovery=True
    device.connect()

When using with pyats, the feature can be used in the following way:

.. code-block:: python

    device = testbed['R1']
    device.connect(prompt_recovery=True)

In pyats, to use `prompt_recovery` in next `connect()` call, use `device.destroy()` to disconnect connection and
use `device.connect(prompt_recovery=True)` again.


Login and Password Prompts
--------------------------

Unicon generic plugin uses the following regular expressions to match login and password prompts:

#. Login pattern: `r'^.*([Uu]sername|[Ll]ogin): ?$'`
#. Password pattern: `r'^.*[Pp]assword( for )?(\S+)?: ?$'`

While creating a connection, Unicon sends username and password when the device prompt matches the above patterns.

In some cases, change in login/password prompts on device may lead to connection failure if the default
patterns no longer match.

To handle such situations, user can provide custom regular expression pattern to match with different
login and password prompts on the device.

It can be done by setting regular expression to `LOGIN_PROMPT` and `PASSWORD_PROMPT` attributes of device `settings`.

Example:

.. code-block:: python

    # Unicon standalone mode
    dev = Connection(hostname='R2', start=['telnet x.x.x.x'],\
        credentials={{'default': {'username': 'admin', 'password': 'Cisc0123'}})
    dev.settings.LOGIN_PROMPT = r'USERNAME:\s?$'
    dev.settings.PASSWORD_PROMPT = r'PASSWORD:\s$'

In pyATS testbed yaml file, this can be set in the following way:

.. code-block:: yaml

    devices:
      R2
        credentials:
            default:
                username: admin
                password: Cisc0123
        connections:
          defaults: {class: 'unicon.Unicon'}
          a:
            protocol: telnet
            ip: x.x.x.x
            port: 2042
            prompts:
                login: "USERNAME:\s*$"
                password: "PASSWORD:\s*$"


The login and password patterns are also applicable for login/password prompts displayed during
`reload()`, `switchover()` services. It is possible to override the login and
password dialogs and other default dialogs in the execute service by specifying the
`service_dialog` option in the execute statement. See `execute service`_.

.. _execute service: services/generic_services.html#execute

This setting attribute are not applicable for `ise` plugin.

These settings attributes are supported on below plugins:

#. generic
#. iosxr
#. junos
#. linux
#. aireos


Learn Device OS
--------------------

Unicon generic plugin now can learn the device os/platform and redirect the connection to use corresponding plugins.
This can be done if you pass `learn_os` argument in `device.connect(learn_os=True)`.

Example:

In pyATS testbed.yaml file, no `os` is provided:

.. code-block:: yaml

    devices:
      Router:
        alias: uut
        type: xe
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
            ip: x.x.x.x
            port: xxxx

In pyATS shell:

.. code-block:: python

    # pyats shell --testbed-file testbed.yaml
    >>> from genie.testbed import load
    >>> testbed = load('testbed.yaml')
    -------------------------------------------------------------------------------            
    >>> dev = testbed.devices['uut']
    >>> dev.connect(learn_os=True)
    # dev.connect()  << if learn_os is not provided, then it will use generic plugin


    device's os is not provided, unicon may not use correct plugins

    2020-08-11 16:17:37,909: %UNICON-INFO: +++ Router logfile /tmp/Router-cli-20200811T161737899.log +++

    2020-08-11 16:17:37,910: %UNICON-INFO: +++ Unicon plugin generic +++
    Trying x.x.x.x...


    2020-08-11 16:17:37,951: %UNICON-INFO: +++ connection to spawn: telnet x.x.x.x xxxx, id: 140643774849992 +++

    2020-08-11 16:17:37,952: %UNICON-INFO: connection to Router

    2020-08-11 16:17:37,952: %UNICON-INFO: Learning device Router os
    Connected to x.x.x.x.
    Escape character is '^]'.

    Router#

    2020-08-11 16:17:38,543: %UNICON-INFO: +++ Router: executing command 'show version' +++
    show version
    Cisco IOS Software, IOS-XE Software (PPC_LINUX_IOSD-ADVIPSERVICES-M), Version 15.2(4)S, RELEASE SOFTWARE (fc4)
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2012 by Cisco Systems, Inc.
    Compiled Mon 23-Jul-12 19:02 by mcpre

    IOS XE Version: 03.07.00.S

    Cisco IOS-XE software, Copyright (c) 2005-2012 by cisco Systems, Inc.
    All rights reserved.  Certain components of Cisco IOS-XE software are
    licensed under the GNU General Public License ("GPL") Version 2.0.  The
    software code licensed under GPL Version 2.0 is free software that comes
    with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
    GPL code under the terms of GPL Version 2.0.  For more details, see the
    documentation or "License Notice" file accompanying the IOS-XE software,
    or the applicable URL provided on the flyer accompanying the IOS-XE
    software.


    ROM: IOS-XE ROMMON

    Router uptime is 31 weeks, 2 hours, 15 minutes
    Uptime for this control processor is 31 weeks, 2 hours, 18 minutes
    System returned to ROM by reload
    System image file is "bootflash:asr1000rp1-advipservices.03.07.00.S.152-4.S.bin"
    Last reload reason: PowerOn


    cisco Router-F (2RU) processor with 1698793K/6147K bytes of memory.
    Processor board ID FOX1405GDVK
    12 Gigabit Ethernet interfaces
    32768K bytes of non-volatile configuration memory.
    4194304K bytes of physical memory.
    7798783K bytes of eUSB flash at bootflash:.

    Configuration register is 0x2102

    Router#

    2020-08-11 16:17:40,221: %UNICON-INFO: Learned device os: iosxe

    2020-08-11 16:17:40,222: %UNICON-INFO: 
    Learned device os: iosxe
    Redirect to corresponding plugins.

    2020-08-11 16:17:52,263: %UNICON-INFO: +++ Router logfile /tmp/Router-cli-20200811T161752253.log +++

    2020-08-11 16:17:52,263: %UNICON-INFO: +++ Unicon plugin iosxe +++
    Trying x.x.x.x...


    2020-08-11 16:17:52,288: %UNICON-INFO: +++ connection to spawn: telnet x.x.x.x xxxx, id: 140643774387984 +++

    2020-08-11 16:17:52,288: %UNICON-INFO: connection to Router
    Connected to x.x.x.x.
    Escape character is '^]'.

    Router#

    2020-08-11 16:17:52,896: %UNICON-INFO: +++ initializing handle +++

    2020-08-11 16:17:52,897: %UNICON-INFO: +++ Router: executing command 'term length 0' +++
    term length 0
    Router#

    2020-08-11 16:17:53,113: %UNICON-INFO: +++ Router: executing command 'term width 0' +++
    term width 0
    Router#

    2020-08-11 16:17:53,310: %UNICON-INFO: +++ Router: executing command 'show version' +++
    show version
    Cisco IOS Software, IOS-XE Software (PPC_LINUX_IOSD-ADVIPSERVICES-M), Version 15.2(4)S, RELEASE SOFTWARE (fc4)
    Technical Support: http://www.cisco.com/techsupport
    Copyright (c) 1986-2012 by Cisco Systems, Inc.
    Compiled Mon 23-Jul-12 19:02 by mcpre

    IOS XE Version: 03.07.00.S

    Cisco IOS-XE software, Copyright (c) 2005-2012 by cisco Systems, Inc.
    All rights reserved.  Certain components of Cisco IOS-XE software are
    licensed under the GNU General Public License ("GPL") Version 2.0.  The
    software code licensed under GPL Version 2.0 is free software that comes
    with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
    GPL code under the terms of GPL Version 2.0.  For more details, see the
    documentation or "License Notice" file accompanying the IOS-XE software,
    or the applicable URL provided on the flyer accompanying the IOS-XE
    software.


    ROM: IOS-XE ROMMON

    Router uptime is 31 weeks, 2 hours, 15 minutes
    Uptime for this control processor is 31 weeks, 2 hours, 18 minutes
    System returned to ROM by reload
    System image file is "bootflash:asr1000rp1-advipservices.03.07.00.S.152-4.S.bin"
    Last reload reason: PowerOn


    cisco Router-F (2RU) processor with 1698793K/6147K bytes of memory.
    Processor board ID FOX1405GDVK
    12 Gigabit Ethernet interfaces
    32768K bytes of non-volatile configuration memory.
    4194304K bytes of physical memory.
    7798783K bytes of eUSB flash at bootflash:.

    Configuration register is 0x2102

    Router#

    2020-08-11 16:17:55,027: %UNICON-INFO: +++ Router: config +++
    config term
    Enter configuration commands, one per line.  End with CNTL/Z.
    Router(config)#no logging console
    Router(config)#line console 0
    Router(config-line)#exec-timeout 0
    Router(config-line)#end
    Router#
    