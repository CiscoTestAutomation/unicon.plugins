Expect Abstraction Library
===========================

Introduction
------------
Expect Abstraction Library (EAL), as the name suggests,  is a python based
avatar of `Tcl/Expect`_ library. This package attempts to bring in most of the
useful features of Expect in a pythonic flavour.

**EAL** provides classes and structures required to programatically control
any *interactive command*. For interactive programs, whose order of
interactions varies based on the user input, we can use **dialogs**. **Dialogs**
can dymamically invoke different callbacks based on the corresponding pattern
match.

EAL provides the lower most abstraction level to **Unicon** to perform device
interactions. This library can be used even outside the context of device
connection, for invocation of general shell commands; for example invoking
an interactive shell program on a linux system.

This library brings in following major API's and settings.

* spawn
* expect
* send
* log_user
* no_transfer
* exp_continue
* dialogs
* timeout

This is how a simple EAL program could look like.

.. code-block:: python
   :linenos:

    from unicon.eal.expect import Spawn
    prompt = r"^.*bash\$$\s?"
    s = Spawn(spawn_command="telnet 1.2.3.4")
    s.expect([r"username:"])
    s.send("admin\r")
    s.expect([r"password:"])
    s.sendline("lab") # same as send but doesn't require carriage return
    s.expect([prompt])
    s.close()

Challenges
----------
Implementing an Expect like library is a bit of task in Python becuase of
following two reasons:

**Event Driven**:  Python, unlike Tcl is not *event driven* language at core.
Becuase of this, python lacks asyncronous event loops. We need asyncronous event
loops for precise tracking of timeouts.

.. note::

    Python 3 included asyncio as a core library for carrying out asyncronous
    tasks.

**Eval**: Python does not encourage evaluation of arbitrary code. Yes it is
allowed, but it should be only used only in situation when standard python
techniques do not work. Whereas it is quite common in Tcl to pass chunks of
code as arguments, which the receiving function can invoke in caller's context.
Because of this self imposed limitation, it is difficult to created nested
**Expect** blocks containing patterns and action/callback pairs.

**Globals**: Globals are strongly discouraged in python. In absence of global
variables we need some special ways to handle situations where we need our
callback functions to communicate with each other.

**EAL** tries its best to overcome these problems and provide an intuitive set
of APIs to handle interactive shell commands.

Why Not Pexpect
---------------

One common question we often receive is:

    Why not `pexpect`_ !

In our benchmark tests we found pexpect to be significantly slower than
Tcl/Expect. The order of difference was enough for us to consider different
possible options. It also lacks concept of *Dialogs*, without which, it is
difficult to scale pexpect programs.

We also included the following libraries in our benchmark tests.

* `Telnetlib`_
* `Exscript`_
* `Paramiko`_

Under The Hood
--------------

*EAL* is developed based on `pty`_ library. Pty is a standard python package
for in-memory handling of pseudo terminals.

Pty library forks a process and provides socket like objects for communicating
 with those processes.

EAL uses this as follows:

* fork a process.
* in the forked process, exec the ssh command which will connect to localhost.
* once we have the shell, issue the command which needs to be spawned.
* forked process returns a file descriptor, use this for inter process communication.
* destroy the process when the scope of spawned command is over.

Currently this option is looking scalable and provides extremely good
performance, almost at par with Tcl/Expect or sometimes even better.

Spawn
-----

You can ``Spawn`` any command to interact with it. Once the command is spawned
you can interact with it using APIs like ``send`` and ``expect``.

This is how, in a nutshell, it works

.. code-block:: python

    from unicon.eal.expect import Spawn
    s = Spawn("telnet 1.2.3.4 1000")
    # now we have spawn object s

    s.send("\r")
    ret = s.expect(['pattern'])


Example Shell Script
--------------------

Since we do not find interactive commands commonly on linux platforms, hence we
will use the following shell program during all our subsequent examples in this
chapter. Please make sure you save the following shell program as ``router.sh``
on your Linux/Mac system. All the example which will follow from here will spawn
``router.sh``. You may require to give it execute permission::

    chmod 755 router.sh

Credentials for the router::

    username: admin
    password: lab
    enable password: lablab

Here is the source code of ``router.sh``:

.. literalinclude:: ../user_guide/examples/router.sh
   :linenos:
   :language: bash

This is a sample run of this script. It is just a minimal script to simulate a
router kind of stuff::

    $ ./router.sh
    Trying X.X.X.X ...
    Escape character is '^]'.
    Press enter to continue ...

    username: admin
    password:
    sim-router>enable
    password: lab
    sim-router#show clock
    Fri Oct 23 01:55:16 IST 2015
    sim-router#

It is only capable to doing following things which is just enough for our
purpose.

* perform a login.
* going to enable mode with enable command.
* running ``show clock`` command.

Spawning Our First Command
--------------------------

Now let us **spawn** the ``router.sh``. This is how it can be done. We are
assuming that ``router.sh`` is in the current directory, or else you can provide
the fully qualified path.

.. code-block:: python

    import os
    from unicon.eal.expect import Spawn
    router_command = os.path.join(os.getcwd(), 'router.sh')
    s = Spawn(router_command)

Following events happen when above code is executed.

* an ssh session to localhost is created. This will be manifested a minimal lag.
* a new tty session is created inside the ssh connection.
* ``router.sh`` is invoked.

.. note::

    You may also see the login banner of localhost, which is normal. This has
    nothing to do with the spawned command.

Using Send Command
------------------

In case you have executed the ``router.sh``, you will notice that it waits for
you to press the ``ENTER`` button, before it can show the username prompt. This
is the exact place where it waits::

    Press enter to continue ...

Hence let us send the the carriage return.

.. code-block:: python

    s.sendline()
    # we can also do it like this.
    s.send("\r")
    # both are equivalent.

``send/sendline`` methods do not return anything, even if they do, it is
irrelevant. Either your command will be sent or an exception will be raised.

Expect The Expected
--------------------

After the sending the carriage return we expect the **username:** prompt. Hence
let us write a pattern to handle this.

.. code-block:: python

    ret = s.expect([r'username:\s?$'])

If the above pattern is not received within the specified amount of time, then
a ``TimeoutError`` is raised. By default, the timeout value is *10*. Let us
reduce it since we know our ``router.sh`` will take almost no time to show
the **username** prompt.

.. code-block:: python

    ret = s.expect([r'username:\s?$'], timeout=5)

Let us generalise the above program a bit. We may come across some routers
where username prompt doesn't look like ``username:``, it may also show up like
``login::``. The good news is, ``expect`` method can take a list of patterns.

.. code-block:: python

    ret = s.expect([r'username:\s?$', r'login:\s?$'], timeout=5)


By default, match_mode_detect is enabled. Detect rules are as below:

1. search whole buffer with re.DOTALL if:

- pattern contains any of: \\r, \\n

- pattern equals to any of: .*, ^.*$, .*$, ^.*, .+, ^.+$, .+$, ^.+

2. If pattern ends with $ but not \$, will only match last line

3. In other situations, search whole buffer with re.DOTALL

Now let's introspect on the return object. The return object contains the
following:

* last_match: the ``re`` match object.
* match_output: the exact text which matched in the buffer.
* last_match_index: the index of pattern in the list which matched.
* last_match_mode: the match mode eg. search whole buffer with re.DOTALL, only match last line

Generally you will be interested in the ``match_output``.

Now lets sum it up and complete the above program to login and run a command.
``show clock``. Most of the program is self explanatory.

.. literalinclude:: ../user_guide/examples/1_eal_simple_sendex.py
   :language: python
   :linenos:

.. note::

    A note on pattern matching and buffer size. The default search size is 8K
    which is used to search up to 8K bytes at the end of the buffer. This speeds
    up pattern matching for very large command output. To specify a different
    search size, use the `search_size` parameter. Using ``0`` will search the
    complete buffer.

    You can check and set the default search size using the `SEARCH_SIZE` setting.

    .. code-block:: python

        ret = s.expect([r'huge pattern .* matching more than 8K'], timeout=60, search_size=16000)

        >>> s.settings.SEARCH_SIZE
        8192
        >>>
        >>> s.settings.SEARCH_SIZE = 16000
        >>> s.settings.SEARCH_SIZE
        16000
        >>>

EOF Exception
-------------

If the spawn connection has terminated/closed (like someone clear console line or
close() is called on spawn) then any call to send/expect will raise an EOF exception.

.. code-block:: python

    from unicon.eal.expect import Spawn
    s = Spawn("telnet 127.0.0.1 15000")
    s.close()
    s.expect([r"username:"]) # This will raise EOF
    s.send('some data') # this will raise EOF
    # Spawn again if EOF raise
    from unicon.core.errors import EOF
    try:
        s.expect(r'.*')
    except EOF as e:
        print('Spawn not available, Re-Spawn.')
        s = Spawn('telnet 127.0.0.1 15000')


Need For Dialogs
----------------

Above programs looks complete, but it has few limitations. We can use
``send/expect`` pair when we know for sure, that sequence of interaction will
never change. Think of a hypothetical situation, in the above example, if the
``router.sh`` prompts for *password* before *username* ! In such situation,
above program will timeout, even though it knows how to handle the password
prompt. The order of interaction cannot be taken for granted in all the
situations.

We need to interact with commands which prompts for different things based on
the user input, and our program should be able to handle it. The better example
could be ``copy`` command on the router. On different platforms, and with
different copy protocols we see different questions being asked. And it is
expected from our API's to handle all such variations, in order to produce a
platform agnostic API.

**Dialogs** provide a way to handle exactly the same situation. It allows us to
club all the anticipated interactions in one structure. It is agnostic to
sequence of interaction as long as dialog knows how to handle it. At semantic
level this how it looks.

.. code-block:: python

    d = Dialog([statement_1,
                statement_2,
                ...,
                ...,
                statement_n])
    # to execute or process a dialog.
    d.process(s)
    # here s is the spawn instance on which this dialog has to
    # be targeted.

In **EAL** Dialog is a class which is constituted of *Statements*. Before we
go forward, lets study ``Statement`` class, the building block of a dialog.

Statements
-----------

Statements are building blocks of Dialogs. It has following constituents.

* **pattern**: pattern for which the statments get triggered. (mandatory)
* **action**: any callable which needs to be called once the pattern is matched. (optional)
* **args**: a dict which contains arguments to *action*, if any. (default value ``None``)
* **loop_continue**: whether to continue the dialog after this statement match. (default value ``False``)
* **continue_timer**: the dialog timeout gets reset after every match. (default value ``True``)
* **debug_statement**: log the matched pattern if set to True. (default value ``False``)
* **trim_buffer**: whether to remove match content from buffer. (default value ``True``)
* **matched_retries**: retry times if statement pattern is matched. (default value 0)
* **matched_retry_sleep**: sleep between retries. (default value 0.02 seconds)

This is how an statement can be constructed.

.. code-block:: python
   :linenos:

    # create a simple callback function
    def send_password(spawn, password):
        spawn.sendline(password)

    from unicon.eal.dialogs import Statement
    s = Statement(pattern=r'password:',
                  action=send_password,
                  args={'password': 10},
                  loop_continue=True,
                  continue_timer=False,
                  trim_buffer=True,
                  debug_statement=True)

Feel free to use lambdas in case you find it convenient for simple operations

.. code-block:: python

    # By using lambda, same thing can be written as below.
    # in this we don't need to define the callback functions.
    from unicon.eal.dialogs import Statement
    s = Statement(pattern=r'password:',
                  action=lambda spawn, password: spawn.sendline(password)
                  args={'password': 10},
                  loop_continue=True,
                  continue_timer=False)

Notice the ``args`` in both the examples. We have not supplied any value for
the argument ``spawn`` even though the callback function (or the lambda) depends
on it. EAL performs dependency injection for few thinngs which cannot be
determined while contructing the ``Statement`` object. We will see it in detail
in the next section.

.. note::

    Mention ``args``, ``loop_continue``, ``continue_timer`` only if you want to
    change the the default values. This will help reducting the clutter.

**Timeout Statement**:
By default, if none of Statement patterns get match within timeout period
``TimeoutError`` execption gets raised. If we want to add some custom action when
timeout occurs before ``TimeoutError`` execption, this can be done by adding a
``Statement`` with pattern set as ``__timeout__``. Action set for this Statement
will get invoke if timeout occurs.

.. code-block:: python

    def custom_timeout_method(spawn):
        print('None of patterns matched within timeout period.')

    s = Statement(pattern='__timeout__',
                  action=custom_timeout_method,
                  loop_continue=False,
                  continue_timer=False)

.. note::

    Make sure to set ``continue_timer`` as ``False`` for timeout statement, else it may
    will end up in infinite loop. If ``continue_timer`` set as ``True``, then ``Dialog`` will
    start trying to match all patterns again and timeout period will be reset to
    original one.


Dependency Injection in Statements
-----------------------------------

Few things which cannot be determined at the time of construction of Statement
objects, are dependency injected by the EAL framework. There are three such
things.

* spawn
* context (an attribute dict)
* session (an attribute dict)

**spawn**:
Since same dialog instance can be used on multiple spawns instances, hence user
cannot determine its (spawn) value at the time creating ``Statement`` instance.
If your callback requires *spawn* then, just mention it in signature.
You dont't need to provide its value in the ``args`` section.

**context**:
It is possible to have a situation when the value of some of the arguments of
the callback needs to be determined at the runtime. One good example could be
fetching the *password* from some config file, on which the developer has no
control. In such situations, same callback function could be written like this.

.. code-block:: python
   :linenos:

    def send_password(spawn, context):
        spawn.sendline(context.password)

    from unicon.utils import AttributeDict
    ctx = AttributeDict({'password': 'lab'})

    from unicon.eal.dialogs import Statement
    s = Statement(pattern=r'password:',
                  action=send_password,
                  loop_continue=True,
                  continue_timer=False)
    # we are assuming we have more statements s1 and s3
    # also we have one spawn instance named s.
    d = Dialog([s, s1, s3])
    d.process(s, context=ctx)

.. note::

    we don't need ``args`` in above statement as both the values will be
    injected in runtime.

**session**: It is used for scenarios where different callback functions in
a dialog would require to communicate with each other. *session* provides a way
for inter callback communication. It is an ``AttributeDict`` which can be
treated as dictionary. It is also required if the same statement matched more
than once during an interaction and the callback function is expected to
behave differently in both the entries. We will have an example for this later.

Whenever a dialog processing begins, a blank ``session`` dict is
initialized. Any callback function can add or access any value to it. Since it
is a dictionary, hence all the rules for handling *dict*s are
applicable. It is strongly recommended to check for the presence of a key before
accessing it. Becuase it can always happen that statement callback function
which was supposed to *set the value* has not been invoked yet. This precaution
will help avoiding ``KeyError``.

To be able to use the session dict we need to mention it in the callback
signature, else it will not be injected.

We will use these concepts in the later part of the document to make things
clear.

Dialogs Revisited
-----------------

In this section we will cover two different ways the dialogs can be created.

.. code-block:: python
   :linenos:

    # as said, dialog is a list of statements
    d = Dialog([
        Statement(pattern=r'^pat1',
                  action=first_callback,
                  args=dict(a=1),
                  loop_continue=True,
                  continue_timer=False),
        Statement(pattern=r'^pat2',
                  action=second_callback,
                  args=None,
                  loop_continue=False,
                  continue_timer=False),
       Statement(pattern=r'^pat3',
                 action=third_callback,
                 args=None,
                 loop_continue=True,
                 continue_timer=False),
    ])

As we can see there is a lot of typing involved. We can also use a shorthand
notation. Same dialog can also be represented as follows.

.. code-block:: python
   :linenos:

    d = Dialog([
        [r'^pat1', first_callback, {'a':1}, True, False],
        [r'^pat2', second_callback, None, False, False],
        [r'^pat3', third_callback, None, True, False],
    ])

Above style is a lot compact. Here we only need to provide arguments required
by the ``Statement`` class as a list. But while using above notation please
make sure to provide all the default arguments in case any of the default
values are changed.

.. note::

    Please make sure to have at least one statement in the dialog having its
    ``loop_continue`` value as False, else the dialog will run into infinite
    loop, till it times out. We can't call it a bug becuase sometimes it is a
    desired feature. But almost always you will not want an infinite loop.

Dialog Shorthand Notation
-------------------------

.. versionadded:: 1.1.0

As you can see above, we are required to write callback function even for
very trivial operations like sending a character `y` or `yes`. Sometimes
writting even little lambda functions also cause a lot of clutter.

It is good to know how callback functions work but for very trivial operations
you can use special string notation to get the the job done. For example if you
need to send a "yes" followed by a new line character. You can do it like this::

    Dialog([
        [r'pattern', 'sendline(yes)', None, False, False]
    ])

As you can see in the above example, you don't need to define `sendline`
function. We have more such *string based callbacks*. You can send any
string by changing the *string* inside the parenthesis. For example to
send `xx` you can write it as `sendline(xx)`.

.. note::

    Please make sure you don't use any quotations line `''` or `""`
    inside the parenthesis.

=====================  ==============================================
String Callbacks       Description
=====================  ==============================================
sendline(x)            sends the `x` followed by a new line character
send(x)                sends the `x` without a new line character
send_ctx(x)            sends the value in the context dict with key `x`, without a new line character.
sendline_ctx(x)        sends the value in the context dict with key `x`, follwed by a new line character
send_session(x)        sends the value in the session dict with key `x`, without a new line character.
sendline_session(x)    sends the value in the session dict with key `x`, followed by a new line character.
sendline_cred_user(x)  sends the username for credential with key `x`, followed by a new line character.
sendline_cred_pass(x)  sends the password for credential with key `x`, followed by a new line character.
=====================  ==============================================

In the next section we would see how to use this in practice.

Putting It All Together
-----------------------

Let us now try to put all the above concepts to work. First we will try the
following assigenment::

    login to the router to reach the disable prompt

The program to handle this could look like this. We will call it our
**version 1**.

.. literalinclude:: ../user_guide/examples/2_dialog_with_three_callbacks.py
   :language: python
   :linenos:
   :emphasize-lines: 10-20

One thing we can quickly notice here, is that all the callback functions look a
like. In the first glance we can say that there is scope for some optimization.
Rather that writting three callback functions, all of which look alike, we can
improve it by using only one callaback function.

Let's see our **version 2**, this is more `DRY`_ than the previous.

.. literalinclude:: ../user_guide/examples/3_dialog_with_one_callback.py
   :language: python
   :linenos:

But there is still room for improvement. In fact, our lone callback function
is essentially performing a very trivial task, i.e sending a command. We can
actually write it *inline* using *lambda functions*. Our **version 3**

.. literalinclude:: ../user_guide/examples/4_using_lambda.py
   :language: python
   :linenos:

Now let's use the *shorthand* notation which we learnt in the last section.
This can make the overall composition look even more compact and lucid. Here
is **version 4**

.. literalinclude:: ../user_guide/examples/5_using_shorthand.py
   :language: python
   :linenos:

Based on your preference you can use either of version 2 or 3 or 4. But we
will strongly recommed to use version *4*, i.e. the one which follows shorthand
notation, whenever and whereever possible. It reduces the chances or including
an erroneous callback function and also avoids code duplication.

Using Session
-------------

Now lets extend the problem a bit::

    What if we have to take the router till enable mode, unlike the previous
    example where we are only going till disable mode.

In the first glance it may just look like a linear extension to the previous
problem, but it is not. It may tempt us to solve it by just adding one more
*statement* in the *dialog*. But notice the fact that *login password prompt*
and *enable password prompt* look the same. Hence the following statement will
trigger twice::

    [r'password:\s?$', send_command, {'command': 'lab'}, False, False]

But on the second occassion it has to send the enable password. We can't have
two statements having the same pattern in a dialog. We need to solve this by
doing something at the callaback level. Our callback must have a way to
understand whether it has been called for the first time or the second time, in
order to decide which password to send. Here we can use ``session`` to our
rescue.

.. literalinclude:: ../user_guide/examples/6_using_session.py
   :language: python
   :linenos:

Similar approch can be taken to solve situations where two callaback in two
different callabacks have to communicate with each other. ``session`` is unique
to the whole dialog context.

The same code can be also we re-written using shorthand notation as follows. We
would recommed you to use this version over the one which was just illustrated.

.. literalinclude:: ../user_guide/examples/7_using_shorthand_with_session.py
   :language: python
   :linenos:

.. _prompt_recovery_label:

Prompt Recovery Feature
------------------------
Prompt recovery feature will try to recover device after normal dialog timeout occurs. This is just an attempt to bring device to stable state and this does not guarantee to bring device to stable state in every scenario.

Use case: Once device booted up with image, console messages displayed over terminal, because of these console log messages over terminal unicon is unable to match the device prompt. Sending a enter key to device bring the device prompt at front and unicon matches device prompt. After reload, console messages can interfere with prompt matching, especially during reload and configuration operations

This feature is available for Dialog, Connect and Services.

**Usage**

By default this feature is disabled. To enable it, use it in this way:

.. code-block:: python

    Dialog.process(spawn, prompt_recovery=True)
    # In Unicon
    device = Connection(hostname='R1', start=['telnet x.x.x.x'], prompt_recovery=True]
    device.connect()
    # In pyATS
    device.connect(prompt_recovery=True)
    device.service(command, prompt_recovery=True)

**Prompt recovery configurations**

prompt_recovery can be configure using below 3 settings:

    * PROMPT_RECOVERY_COMMANDS : List of prompt recovery commands.
      Default value: `['\\r', '\\025', '\\032', '\\r', '\\x1E']`. '\\025' is Ctrl-U, '\\032' is Ctrl-Z and '\\x1E' is Ctrl-^
      For Linux connection type default command list is: `['\\r', '\\x03', '\\r']`
      `\\x03` is Ctrl-C.
    * PROMPT_RECOVERY_INTERVAL : Timeout period after sending each prompt recovery command, in secs.
      Default value: 10 secs
    * PROMPT_RECOVERY_RETRIES  : Number of prompt recovery retires to perform.
      Default value: 1

Users can also alter these values at run time by setting these values as dialog context.

Example:

.. code-block:: python

    from unicon.utils import AttributeDict
    ctx = AttributeDict()
    ctx.prompt_recovery_interval = 30
    dialog.process(dev.spawn, context = ctx)

``dialog`` is Dialog object.
``dev`` is device connection object.

**Working of prompt recovery feature**

When prompt_recovery is enable, below steps followed:

#. After normal Dialog Timeout occurs. Unicon will not return Timeout exception at that moment,
   it will try to recover it to known state. Here known state means, try to match all the patterns
   in dialog again after sending `PROMPT_RECOVERY_COMMANDS` to device.
#. List of command which are set to `PROMPT_RECOVERY_COMMANDS` are send to device, one at a time
   and new timeout period is set, value of this new timeout period is `PROMPT_RECOVERY_INTERVAL`.
#. After sending each `PROMPT_RECOVERY_COMMANDS` command, unicon waits if device comes to any known
   stable state. If device comes to any of known stable state, Dialog processing is complete and
   dialog process is considered as successful.
#. After sending all `PROMPT_RECOVERY_COMMANDS` commands to device, one at a time, if device does
   not comes to known stable state then Timeout exception will be raised.
#. Step 2 will get repeated `PROMPT_RECOVERY_RETRIES` times. Example, Value of 1 to `PROMPT_RECOVERY_RETRIES`
   means, all commands set to `PROMPT_RECOVERY_COMMANDS` will be sent to device once. If its set as 2,
   then all commands will be send two times and the sequence of commands will be like below

.. code-block:: text

   PROMPT_RECOVERY_COMMANDS = [cmd1, cmd2, cmd3]
   PROMPT_RECOVERY_RETRIES = 2

Commands to device will be send in below sequence to device

.. code-block:: text

   cmd1, cmd2, cmd3, cmd1, cmd2, cmd3


..    log_user                            X
..    no transfer                         X
..     exp_internal                        X
..     changing sessions.                  X
..     using regexes with end marker       X
..     Thread Saftey                       X

.. _pty: https://docs.python.org/3.2/library/pty.html
.. _DRY: https://en.wikipedia.org/wiki/Don%27t_repeat_yourself
.. _Tcl/Expect: http://www.tcl.tk/man/expect5.31/expect.1.html
.. _Telnetlib: https://docs.python.org/2/library/telnetlib.html
.. _Paramiko: http://www.paramiko.org
.. _Exscript: https://github.com/knipknap/exscript
.. _pexpect: https://pexpect.readthedocs.org
