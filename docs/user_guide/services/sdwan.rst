SDWAN
======

The Software Defined Wide Area Network (SDWAN) OS plugin (`sdwan`) supports ``viptela`` devices.

If you are using SDWAN on Viptela platforms, specify either one of below configs, they use the same plugin implementation.

.. code-block:: yaml

      sdwan1:
        os: sdwan
        platform: viptela
        connections:
          cli:
            protocol: ssh
            ip: 1.2.3.4

.. code-block:: yaml

      sdwan2:
        os: viptela
        connections:
          cli:
            protocol: ssh
            ip: 1.2.3.4


This section lists the services which are supported:

  * `reload <#reload>`__

Both plugins support below generic services:

  * `execute <generic_services.html#execute>`__
  * `configure <generic_services.html#configure>`__
  * `send <generic_services.html#send>`__
  * `sendline <generic_services.html#sendline>`__
  * `expect <generic_services.html#expect>`__
  * `log_user <generic_services.html#log-user>`__


reload
------

Reload service for the sdwan/viptela plugin. When used on the console will return the reboot log.
Console sessions will be detected automatically based on the logs observed during the initial connection.

==============   ======================    =====================================================
Argument         Type                      Description
==============   ======================    =====================================================
reload_command   str                       command to execute to reload the device
timeout          int (default 600 sec)     (optional) timeout value for the overall interaction.
reply            Dialog                    (optional) additional dialog object
==============   ======================    =====================================================

.. code-block:: python

    # When running on the console, the boot log will be returned.
    boot_log = viptela.reload()


.. sectionauthor:: Dave Wapstra <dwapstra@cisco.com>

