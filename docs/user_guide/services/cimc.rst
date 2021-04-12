CIMC
====

This section lists the services which are supported on Cisco Integrated Management Console (CIMC).

  * `execute <#execute>`__

The following generic services are also available:

  * `send`_
  * `sendline`_
  * `expect`_

.. _send: generic_services.html#send
.. _sendline: generic_services.html#sendline
.. _expect: generic_services.html#expect


execute
-------

This service is used to execute arbitrary commands on the device. Though it is
intended to execute non-interactive commands. In case you wanted to execute
interactive command use `reply` option.


===============   ======================    ========================================
Argument          Type                      Description
===============   ======================    ========================================
timeout           int (default 60 sec)      timeout value for the overall interaction.
reply             Dialog                    additional dialog
command           str                       command to execute
===============   ======================    ========================================

`Execute` service returns the output of the command in the string format
or it raises an exception. You can expect a SubCommandFailure
error in case anything goes wrong.



.. code-block:: python

        #Example
        --------

        from unicon import Connection
        c=Connection(hostname='server',
                        start=['ssh server'],
                        os='cimc')

        output = c.execute("show chassis")

