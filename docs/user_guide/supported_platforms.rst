Supported Platforms
===================

At the moment `unicon.plugins` supports the following network device types, 
described as their OS (network operation system), series (platform series), and
model (specific model support). 

These values help Unicon load the most accurate connection plugin for the given
network device, and corresponds to ther pyATS testbed YAML counterparts.

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
    ``iosxe``
    ``iosxe``, ``cat3k``
    ``iosxe``, ``cat3k``, ``ewlc``
    ``iosxe``, ``csr1000v``
    ``iosxe``, ``csr1000v``, ``vewlc``
    ``iosxe``, ``sdwan``
    ``iosxr``
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
    ``nso``
    ``staros``
    ``vos``
    ``junos``

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
