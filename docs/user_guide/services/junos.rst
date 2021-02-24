Junos
=====

This section lists down all those services which are only specific to Junos.

  * `configure <#configure>`__

For a list of all the other services please refer to
:doc:`Common Services  <generic_services>`.

.. note::

    Currently supports simplex ( non-HA ) devices only.


configure
---------

For more information see `configure <generic_services.html#configure>`__

The default commit command for Junos is `commit synchronize`.

If you want to configure the device without automatically executing the commit command,
you can override the `commit_cmd` attribute for the configure service in the topology
file or set the `commit_cmd` service attribute in python directly.

.. code:: yaml

    # Example override of commit_cmd for configure service

    devices:
      EX1:
        os: junos
        type: router
        connections:
          cli:
            protocol: telnet
            ip: 127.0.0.1
            port: 64001
            service_attributes:
              configure:
                commit_cmd: ""


.. code:: python

    dev.configure.commit_cmd = ""
    dev.configure('config commands')
    dev.configure('more config commands')
    dev.configure('commit')
