Supported Platforms
===================

At the moment `unicon.plugins` supports the following network device types, 
described as their OS (network operation system), series (platform series), and
model (specific model support). 

These values help Unicon load the most accurate connection plugin for the given
network device, and corresponds to ther pyATS testbed YAML counterparts.

For example, if ``os=iosxe`` and ``series=abc``, since ``abc`` is not found in 
the iosxe table, it will fallback to use the generic ``iosxe`` plugin. If 
``os=iosxe`` and ``series=cat3k``, it will use the specific plugin ``iosxe/cat3k``.

.. tip::

  The priority to pick up which plugin is: chassis_type > os > series > model.


.. csv-table:: Unicon Supported Platforms
    :align: center
    :widths: 20, 20, 20, 40
    :header: "os", "series", "model", "Comments"

    ``aci``, ``apic``
    ``aci``, ``n9k``
    ``aireos``
    ``asa``
    ``asa``, ``asav``
    ``cheetah``, ``ap``
    ``cimc``
    ``confd``
    ``confd``, ``esc``
    ``confd``, ``nfvis``
    ``fxos``
    ``fxos``, ``ftd``
    ``ios``, ``ap``
    ``ios``, ``iol``
    ``ios``, ``iosv``
    ``ios``, ``pagent``,,"See example below."
    ``iosxe``
    ``iosxe``, ``cat3k``
    ``iosxe``, ``cat3k``, ``ewlc``
    ``iosxe``, ``cat9k``
    ``iosxe``, ``csr1000v``
    ``iosxe``, ``csr1000v``, ``vewlc``
    ``iosxe``, ``sdwan``
    ``iosxr``
    ``iosxr``, ``asr9k``
    ``iosxr``, ``iosxrv``
    ``iosxr``, ``iosxrv9k``
    ``iosxr``, ``moonshine``
    ``iosxr``, ``ncs5k``
    ``iosxr``, ``spitfire``
    ``ise``
    ``linux``, , , "Generic Linux server with bash prompts"
    ``nxos``
    ``nxos``, ``mds``
    ``nxos``, ``n5k``
    ``nxos``, ``n9k``
    ``nxos``, ``nxosv``
    ``nxos``, ``aci``, ``n9k``, "Identical to os=aci, series=n9k"
    ``nso``
    ``sdwan``, ``viptela``,,"Identical to os=viptela."
    ``sros``
    ``staros``
    ``vos``
    ``junos``
    ``sros``
    ``viptela``,,,"Identical to os=sdwan, series=viptela."
    ``windows``

To use this table - locate your device's os/series/model information, and fill 
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

  in the above example, ``series`` and ``model`` is not provided, hence Unicon
  will use the most generic ``os==iosxe`` connection implementation for my 
  device.



Example: Single Router
----------------------

.. code-block:: yaml

    devices:
      router_hostname:
        os: iosxe
        series: csr1000v
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
        series: n9k
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
------------------

**Stack router has connections peer_1, peer_2, peer_3**

.. code-block:: yaml

    devices:
      router_hostname:
        os: iosxe
        series: cat3k
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
------------------

**Quad Sup router has two chassis 1, 2 and 4 connections a, b, c, d**

.. code-block:: yaml

    devices:
      router_hostname:
        os: iosxe
        series: cat9k
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
        series: 'pagent'
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
