NXOS/MDS
========

This section lists down all those services which are only specific to NXOS/MDS platforms.


tie
---

Service to execute commands on the Target Initiator Emulator (TIE)

==========   ========================    =================================================
Argument     Type                        Description
==========   ========================    =================================================
command      str or list (default [])    string or list of commands
timeout      int (default 60 sec)        timeout in sec for executing command on shell.
target       standby/active              by default commands will be executed on active,
                                         use target=standby to execute command on standby.
==========   ========================    =================================================

.. code-block:: python

    cmd = ['cmd1', 'cmd2']
    sw.tie(cmd)

You can use this service as a context manager.

.. code-block:: python

    with sw.tie() as tie:
        tie.execute('cmd')
