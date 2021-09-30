IOSXE
=====

This section lists down all those services which are only specific to IOSXE.
For list of all the other service please refer this:
:doc:`Common Services  <generic_services>`.

rommon
------

Service to bring the device to rommon mode and execute commands (optional).
If commands are specified, the router will be brought to rommon mode and
the commands will be executed. If no commands are specified,
the router will be brought to rommon mode only.

To bring the router back to enable mode, you can use the `enable()` service.
See examples below.

The command to be executed can be passed as a multiline string or a list.

===============   =======================     ========================================
Argument          Type                        Description
===============   =======================     ========================================
command           str or list                 command(s) to be issued on device.
reply             Dialog                      additional dialogs/new dialogs which are not handled by default.
timeout           int                         timeout value in sec, Default Value is 600 sec
prompt_recovery   bool (default False)        Enable/Disable prompt recovery feature
===============   =======================     ========================================

    return :
        * (str) command output

.. code-block:: python

        # bring device to rommon mode
        rtr.rommon()

        # specify timeout to bring device to rommon mode
        rtr.rommon(timeout=1800)

        # execute command in rommon mode
        rtr.rommon('MANUAL_BOOT=yes')

        # bring router to rommon mode
        rtr.rommon()

        # execute rommon command
        rtr.execute('MANUAL_BOOT=yes')

        # If the router is in rommon mode, you can use enable()
        # to bring router to enable mode

        # boot with default boot command
        rtr.enable()
        # boot with specified image
        rtr.enable(image='flash:packages.conf')
