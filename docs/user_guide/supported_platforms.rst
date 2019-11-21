Supported Platforms
===================

At the moment `unicon.plugins` supports the following platforms.
Platform name means os, series and model.
They are used in testbed.yaml or Connection object. (See examples below)

    - ``aci/apic``
    - ``aci/n9k``
    - ``aireos``
    - ``asa``
    - ``asa/asav``
    - ``cheetah/ap``
    - ``cimc``
    - ``confd``
    - ``confd/esc``
    - ``confd/nfvis``
    - ``fxos``
    - ``fxos/ftd``
    - ``ios/ap``
    - ``ios/iol``
    - ``ios/iosv``
    - ``iosxe``
    - ``iosxe/cat3k``
    - ``iosxe/cat3k/ewlc``
    - ``iosxe/csr1000v``
    - ``iosxe/csr1000v/vewlc``
    - ``iosxe/sdwan``
    - ``iosxr``
    - ``iosxr/iosxrv``
    - ``iosxr/iosxrv9k``
    - ``iosxr/moonshine``
    - ``iosxr/ncs5k``
    - ``iosxr/spitfire``
    - ``ise``
    - ``linux``
    - ``nxos``
    - ``nxos/mds``
    - ``nxos/n5k``
    - ``nxos/n9k``
    - ``nxos/nxosv``
    - ``nso``
    - ``staros``
    - ``vos``
    - ``junos``


Example: Single Router
----------------------

.. code-block:: text

    iosxe/csr1000v/vewlc
      |     |       |
      os  series  model

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

.. code-block:: text

    nxos/n9k
     |    |
     os series

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


Example: Linux Server
---------------------

.. code-block:: text

    linux
      |
      os

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
