Password Handling
=================

Passwords are defined in the testbed YAML file. This document describes the
password handling logic used by the different plugins.
For understanding the password handling first we need to understand credentials on pyATS.

.. _credentails:

Credentials
-----------

The ``credentials`` connection parameter defines a dictionary of named
credentials.  A credential is a dictionary typically containing both
``username`` and ``password`` keys.

The ``login_creds`` connection parameter defines an optional sequence of
credential names to try.  Each time the device prompts for a username or
password, the current credential is set to the next credential in the sequence
if a current credential has not already been set.
When a password is sent, the current credential is unset.  The one exception
is when entering an administrator's password on a routing device coming up
without configuration, in this case the current credential is reused.
If the sequence has been exhausted and no more credentials are available to
satisfy a username/password prompt, a
`CredentialsExhaustedError<unicon.core.errors.CredentialsExhaustedError>` is
raised.

Credentials are not retried, any username or password failure causes a
`UniconAuthenticationError<unicon.core.errors.UniconAuthenticationError>`
to be raised.

It is possible to specify the password to use for routing devices to enter
enable mode.  This may be done via the ``enable_password`` entry under the
current credential, or via a separate credential called ``enable``.
Please see :ref:`unicon_enable_password_handling` for details.

Passwords specified as a :ref:`secret_strings` are automatically decoded prior
to being sent to the device.

In pyATS Testbed YAML
"""""""""""""""""""""

Credentials may be specified on a per-testbed, per-device or per-connection
basis, as documented in :ref:`topology_credential_password_modeling`.


.. code-block:: python

    from pyats.topology import loader
    tb = loader.load("""
        devices:
            my_device:
                type: router
                credentials:
                    default:
                        username: admin
                        password: Cisc0123
                    alternate:
                        username: alt_username
                        password: alt_password
                    termserv:
                        username: tsuser
                        password: tspw
                    enable:
                        password: enablepw
                connections:
                    defaults: {class: 'unicon.Unicon'}
                    a:
                      protocol: ssh
                      ip: 10.64.70.11
                      port: 2042
                      login_creds: [termserv, default]
                      ssh_options: "-v -i /path/to/identityfile"

    """)
    dev = tb.devices.my_device
    dev.connect()

    # To connect using different credentials than is contained in the
    # testbed YAML ``login_creds`` key:
    dev.destroy()
    dev.connect(login_creds=['termserv', 'alternate'])


In Python
"""""""""

.. code-block:: python

    dev = Connnection(hostname=uut_hostname,
                       start=[uut_start_cmd],
                       credentials={\
                           {'default': {'username': 'admin', 'password': 'Cisc0123'}},\
                           {'enable': {'password': 'enablepw'}},\
                           {'termserv': {'username': 'tsuser', 'password': 'tspw'}},\
                       },
                       login_creds = ['termserv', 'default'],
                     )


Post credential action
""""""""""""""""""""""

In certain cases, e.g. when using a serial console server, an action is needed to get a response
from the device connected to the serial port. There are two ways to configure this action.
The first one is using a setting, the second one is using a post credential action.
The post credential action takes precedence over the setting.

Example credentials for a device.

.. code-block:: yaml

      my_device:
          type: router
          credentials:
              default:
                  username: admin
                  password: Cisc0123
              terminal_server:
                  username: tsuser
                  password: tspw


Setting the credential action via `settings` in python.

.. code-block:: python

    # Name of the credential after which a "sendline()" should be executed
    dev.settings.SENDLINE_AFTER_CRED = 'terminal_server'


Settings can also be specified for the connection in the topology file as shown below.

.. code-block:: yaml

    connections:
      cli:
        settings:
          SENDLINE_AFTER_CRED: terminal_server


The post credential action supports ``send`` and ``sendline``, you can specify a string to be sent,
e.g. `send( )` to send a space or `send(\\x03)` to send Ctrl-C. Quotes should not be specified.

.. code-block:: yaml

    connections:
      cli:
        login_creds: [terminal_server, default]
        arguments:
          cred_action:
            terminal_server:
              post: sendline()



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
Please see :ref:`credentails` for more details.

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

Fallback Credentials
--------------------

In case of authentication failure,
 you could use fallback credentials before erroring out.
you could have a couple of login credentials and define them using fallback credentials.
These login credentials will be used in sequence. If none of the combination works on the device
we get the bad password exception.

you could have a default list for all the connections in the testbed:

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
            set_1:
              password: lab
              username: lab
            set_2:
              password: admin
              username: admin
        connections:
            defaults:
              class: unicon.Unicon
              fallback_credentials:
                - set1
                - set2
            netconf:
              class: yang.connector.Netconf
              ip: 1.2.3.4
              port: 830
              protocol: netconf
            telnet:
              ip: 1.2.3.4
              port: 23
              protocol: telnet

or you could define fallback credentails per connection:

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
            netconf:
              class: yang.connector.Netconf
              ip: 1.2.3.4
              port: 830
              protocol: netconf
              fallback_credentials:
                  - set_1
              credentials:
                  default:
                      username: cisco
                      password: secret
                  set_1:
                    password: lab
                    username: lab
            telnet:
              ip: 1.2.3.4
              port: 23
              protocol: telnet
              fallback_credentials:
                - set_2
              credentials:
                  default:
                      username: cisco
                      password: secret
                  set_2:
                    password: admin
                    username: admin

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