Password Handling
=================
Please see :ref:`unicon_credentials` for details on how credentials are
specified and on credential sequencing.

Passwords are defined in the testbed YAML file. This document describes the
password handling logic used by the different plugins.

Unicon supports passwords specified in encrypted form.  Please see
:ref:`topology_credential_password_modeling` for details.

Typically, credentials may be specified using any preferred name.

However, the following credentials are specified using well-known reserved
names:

    * ``default`` : The default credential, which is the fallback if a named
      credential is not specified.

    * ``enable`` : The password sent when bringing a routing device to enable mode.
      Please see :ref:`unicon_enable_password_handling` for details.

    * ``sudo`` : The fxos/ftd plugin requires this (see note below).

    * ``ssh`` : Used to authenticate against an ssh tunnel server.
      See :ref:`unicon_ssh_tunnel` for details.

    * ``bmc`` : The iosxr/spitfire plugin requires this (see note below).

These passwords can be defined in the testbed YAML file in the `testbed`
section, for each `device`, or at the connection level.

.. code-block:: yaml

    # generic passwords
    testbed:
        credentials:
            default:
                username: admin
                password: cisco123
            enable:
                password: my_enable_pw


The usage of these credentials depends on the plugin.
The generic plugin is used when no ``os`` is specified in the testbed YAML file.
The generic implementation is used also by most other
plugins except (currently) the `linux` and `asa` plugins.

.. code-block:: yaml

    devices:
      lnx:
        type: linux
        os: linux
        credentials:
            default:
                username: cisco
                password: cisco

If ``username`` is not defined in the credentials, the default username for
Linux is the OS user that is running the python script.
The default linux password is empty ("").

For all other devices, the default password logic is used (unless otherwise
specified by the specific plugin).

``login_creds`` is used to describe the order of credentials to use on
initial login.  If not specified, the ``default`` credential is used.
Please see :ref:`unicon_credentials` for more details.

.. code-block:: yaml

    devices:
      my_device:
        type: router
        os: ios
        credentials:
            default:
                username: cisco
                password: secret
            enable:
                password: enable
        connections:
          vty1:
            credentials:
                default:
                    username: cisco1
                    password: secret1
          vty2:
            credentials:
                first:
                    username: first_user
                    password: first_pw
                default:
                    username: cisco2
                    password: secret2
                enable:
                    password: enable2
                login_creds: [first, default]

.. _unicon_enable_password_handling:

Enable password handling
------------------------

The following example shows a case where a device may have multiple enable
passwords.
For example, different credentials could apply depending on whether or not a
RADIUS server is reachable.

.. code-block:: yaml

    devices:
      my_device:
        type: router
        os: ios
        credentials:
            default:
                username: cisco
                password: secret
                enable_password: enable
            local:
                username: cisco_local
                password: secret_local
                enable_password: enable_local

The following command connects to the router and enters enable mode using
``local`` credential authentication:

.. code-block:: python

    device.connect(login_creds='local')

The following command connects to the router and enters enable mode using
``default`` credential authentication:

.. code-block:: python

    device.connect()

How enable password is chosen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a router asks for an enable password, the password sent is determined
by the following checks.  If all checks are done and still no enable password
is found then an exception is raised.

#. The ``enable_password`` field of the credential specified by the
   ``login_creds`` in the connect call.
#. The ``default`` credential ``enable_password``
#. The ``enable`` credential ``password`` (legacy)
#. The ``default`` credential ``password`` (legacy)


Password sequences in service calls
-----------------------------------

Several services, including ``reload`` and ``switchover``, accept a
credential list that is used to authenticate against a sequence of
username/password prompts encountered while the service is running.


Authentication Failure
----------------------

The following response pattern generates a bad password exception:

.. code-block:: python

    bad_passwords = r'^.*?% (Bad passwords|Access denied|Authentication failed)'


Environment variables
---------------------

You can use the environment variable syntax in the topology file so you don't
have to store passwords on the filesystem.

.. code-block:: yaml

  credentials:
    default:
      username: "%ENV{PYATS_USERNAME}"
      password "%ENV{PYATS_USERNAME}"
    enable:
      password "%ENV{PYATS_ENABLE_PASS}"


Passwords on HA enabled devices
-------------------------------

Credentials are specified against the ``a:`` connection for HA enabled devices:


.. code-block:: yaml

    devices:
      ha_device
        type: router
        os: ios
        credentials:
            default:
                username: cisco
                password: secret
            enable:
                password: enable
        connections:
          a:
            credentials:
                default:
                    username: cisco1
                    password: secret1
            protocol: telnet
            ip: 1.1.1.1
            port: 2001
          b:
            protocol: telnet
            ip: 1.1.1.1
            port: 2002




Linux password logic
--------------------

When connecting to the device, the password from the current credential is used.
If another password prompt appears during command execution,
no response is sent and the command will timeout by default.

To execute commands using `sudo`, use the ``sudo`` service. See
:ref:`linux_sudo`

If connecting via ssh, the username of the currently logged in user is used
by default if not otherwise specified via credentials or via ``command``
or ``ssh_options`` keys in one of the following forms:

``ssh -l username <address>`` or ``ssh username@<address>``.

In order to execute a command that leads to a username/password prompt,
you must explicitly add the password statement to the reply Dialog.
If the default password statement is used (as in the example shown below),
a single username/password prompt is responded to using the ``default``
credential.

Example code using the password statement:

.. code-block:: python

    from unicon.eal.dialogs import Dialog
    from unicon.plugins.generic.statements import password_stmt

    dialog = Dialog()
    dialog.append(password_stmt)

    device.execute('command that prompts for password', reply=dialog)


ASA password logic
------------------

If the pattern `'^.+?@.+?'s +password: *$'` is seen, the password of the
current credential is sent.

If the pattern `'^.*Password:\s?$'` is seen, the password of the
``enable`` credential is sent.

Please see :ref:`unicon_enable_password_handling` for details.


iosxr/Spitfire password logic
-----------------------------

The typical credential sequence is used to authenticate against each
username/password request from the device.

However, if a BMC login prompt is seen, the password used is taken from the
``bmc`` credential instead.


fxos/ftd password logic
-----------------------

When transitioning from ftd_expert to ftd_expert_root state, the password from the ``sudo`` credential is sent if specified.
Otherwise, the password from the ``default`` credential is sent.  Otherwise, a
`UniconAuthenticationError<unicon.core.errors.UniconAuthenticationError>` is raised.

nxos password logic
-------------------

The ``switchto`` service accepts a ``vdc_cred`` argument that identifies a
named credential to use to authenticate against the VDC.

SSH passphrase
--------------

You can specify the ``passphrase`` that will be used to respond to the `Enter passphrase for key` prompt
as part of the credential block.

.. code-block:: yaml

    devices:
      my_device:
        type: router
        os: ios
        credentials:
            default:
                username: cisco
                password: secret
                passphrase: secret phrase


SSH Options
-----------

You can specify additional SSH options (such as identity/key files) using the
`ssh_options` key as part of the connection block:

.. code-block:: yaml

    devices:
      my_device:
        type: router
        os: ios
        connections:
            vty:
                protocol: ssh
                ip: 10.64.70.11
                port: 2042
                ssh_options: "-i /path/to/id_rsa -o UserKnownHostsFile /dev/null"