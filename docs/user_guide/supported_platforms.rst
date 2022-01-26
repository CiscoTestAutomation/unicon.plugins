Supported Platforms
===================

At the moment `unicon.plugins` supports the following network device types,
described as their OS (network operation system), platform and
model (specific model support).

These values help Unicon load the most accurate connection plugin for the given
network device, and corresponds to ther pyATS testbed YAML counterparts.

For example, if ``os=iosxe`` and ``platform=abc``, since ``abc`` is not found in
the iosxe table, it will fallback to use the generic ``iosxe`` plugin. If
``os=iosxe`` and ``platform=cat3k``, it will use the specific plugin ``iosxe/cat3k``.

.. tip::

  The priority to pick up which plugin is: chassis_type > os > platform > model.


.. csv-table:: Unicon Supported Platforms
    :align: center
    :widths: 20, 20, 20, 40
    :header: "os", "platform", "model", "Comments"

    ``apic``
    ``aireos``
    ``asa``
    ``asa``, ``asav``
    ``asa``, ``fp2k``
    ``cheetah``, ``ap``
    ``cimc``
    ``comware``
    ``confd``
    ``confd``, ``esc``
    ``confd``, ``nfvis``
    ``fxos``,,,"Tested with FP2K."
    ``fxos``, ``fp4k``
    ``fxos``, ``fp9k``
    ``fxos``, ``ftd``,,"Deprecated, please use one of the other fxos plugins."
    ``gaia``, , , "Check Point Gaia OS"
    ``hvrp``
    ``ios``, ``ap``
    ``ios``, ``iol``
    ``ios``, ``iosv``
    ``ios``, ``pagent``,,"See example below."
    ``iosxe``
    ``iosxe``, ``cat3k``
    ``iosxe``, ``cat3k``, ``ewlc``
    ``iosxe``, ``cat8k``
    ``iosxe``, ``cat9k``
    ``iosxe``, ``c9800``
    ``iosxe``, ``c9800``, ``ewc_ap``
    ``iosxe``, ``csr1000v``
    ``iosxe``, ``csr1000v``, ``vewlc``
    ``iosxe``, ``iec3400``
    ``iosxe``, ``sdwan``
    ``iosxr``
    ``iosxr``, ``asr9k``
    ``iosxr``, ``iosxrv``
    ``iosxr``, ``iosxrv9k``
    ``iosxr``, ``moonshine``
    ``iosxr``, ``ncs5k``
    ``iosxr``, ``spitfire``
    ``ironware``
    ``ise``
    ``linux``, , , "Generic Linux server with bash prompts"
    ``nd``, , , "Nexus Dashboard (ND) Linux server. identical to os: linux"
    ``nxos``
    ``nxos``, ``mds``
    ``nxos``, ``n5k``
    ``nxos``, ``n7k``
    ``nxos``, ``n9k``
    ``nxos``, ``nxosv``
    ``nxos``, ``aci``
    ``nso``
    ``sdwan``, ``viptela``,,"Identical to os=viptela."
    ``sros``
    ``staros``
    ``vos``
    ``junos``
    ``eos``
    ``sros``
    ``viptela``,,,"Identical to os=sdwan, platform=viptela."
    ``windows``

To use this table - locate your device's os/platform/model information, and fill
your pyATS testbed YAML with it:

.. code-block:: yaml

    # Example
    # -------
    #
    #   testbed yaml for a single device using Unicon

    devices:
      my-device:
        os: iosxe
        connections:
          cli:
            protocol: ssh
            ip: 1.2.3.4


.. tip::

  in the above example, ``platform`` and ``model`` is not provided, hence Unicon
  will use the most generic ``os=iosxe`` connection implementation for my
  device.



Example: Single Router
----------------------

.. code-block:: yaml

    devices:
      router_hostname:
        os: iosxe
        platform: csr1000v
        model: vewlc
        type: iosxe
        credentials:
          default:
            username: xxx
            password: yyy
          enable:
            password: zzz
        connections:
          a:
            protocol: telnet
            ip: 1.1.1.1
            port: 17017
          vty:
            protocol: ssh
            ip: 2.2.2.2


Example: HA router
------------------

**HA router has connections a and b**

.. code-block:: yaml

    devices:
      router_hostname:
        os: nxos
        platform: n9k
        type: nxos
        credentials:
          default:
            username: xxx
            password: yyy
          enable:
            password: zzz
        connections:
          a:
            protocol: telnet
            ip: 1.1.1.1
            port: 17017
          b:
            protocol: telnet
            ip: 1.1.1.1
            port: 17018
          vty:
            protocol: ssh
            ip: 2.2.2.2


Example: Stack router
---------------------

**Stack router has connections peer_1, peer_2, peer_3**

.. code-block:: yaml

    devices:
      router_hostname:
        os: iosxe
        platform: cat3k
        type: iosxe
        chassis_type: stack            <<< define the chassis_type as 'stack'
        credentials:
          default:
            username: xxx
            password: yyy
          enable:
            password: zzz
        connections:
          defaults:
            class: unicon.Unicon
            connections: [peer_1, peer_2, peer_3]  <<< define the connections to use
          peer_1:
            protocol: telnet
            ip: 1.1.1.1
            port: 2001
            member: 1    <<< peer rp id
          peer_2:
            protocol: telnet
            ip: 1.1.1.1
            port: 2002
            member: 2    <<< peer rp id
          peer_3:
            protocol: telnet
            ip: 1.1.1.1
            port: 2003
            member: 3    <<< peer rp id


Example: Quad Sup router
------------------------

**Quad Sup router has two chassis 1, 2 and 4 connections a, b, c, d**

.. code-block:: yaml

    devices:
      router_hostname:
        os: iosxe
        platform: cat9k
        type: iosxe
        chassis_type: quad             <<< define the chassis_type as 'quad'
        credentials:
          default:
            username: xxx
            password: yyy
          enable:
            password: zzz
        connections:
          defaults:
            class: unicon.Unicon
            connections: [a, b, c, d]  <<< define the connections to use
          a:
            protocol: telnet
            ip: 1.1.1.1
            port: 2001
            member: 1    <<< chassis id
          b:
            protocol: telnet
            ip: 1.1.1.1
            port: 2002
            member: 2    <<< chassis id
          c:
            protocol: telnet
            ip: 1.1.1.1
            port: 2003
            member: 1    <<< chassis id
          d:
            protocol: telnet
            ip: 1.1.1.1
            port: 2004
            member: 2    <<< chassis id


Example: Linux Server
---------------------

.. code-block:: yaml

    devices:
      linux_name:
        os: linux
        type: linux
        credentials:
          default:
            username: xxx
            password: yyy
        connections:
          linux:
            protocol: ssh
            ip: 2.2.2.2


Example: IOS Pagent
-------------------

The ios/pagent plugin requires the ``pagent_key`` to be specified
as an argument to connection.  When the device transitions to enable state
the plugin enters the pagent key for you.

.. code-block:: yaml

   device.connect(pagent_key='123412341234')

Alternatively, you could specify the pagent key as an argument in your
pyATS testbed YAML:

.. code-block:: yaml

    # Example
    # -------
    #
    #   testbed yaml for a single pagent device using Unicon

    device1:
        os: 'ios'
        platform: 'pagent'
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
              pagent_key: '123412341234'
