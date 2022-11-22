.. _mock:

Develop & Run Unittests
=======================

It is strongly recommended to write unittest for plugins to ensure proper test coverage.

**asyncssh is required for running unittest.**

run the following command on the shell::

    pip install asyncssh


A mock device framework is available that uses YAML files as its primary source of 'mocked data'.  
You can also create python methods as part of the mock data class to create specific device behavior.
For more information on YAML syntax, see `yaml.org`_.

.. _yaml.org: http://yaml.org/

The mock device class is part of the `unicon.mock.mock_device` module. The YAML files are located under the
`unicon.plugins.tests.mock_data` directory. Each OS type has its own sub-directory for mock data.


Creating Mock Device
--------------------

A new mock device can be created by executing the `mock_device_cli` command with the `--os`
and `--state` options or by creating a new module with the name
`mock_device_<os_type>.py` and sub classing the mock device class MockDevice.
Mock data needs to be available in YAML files before the mock device can be executed.

Example mock device sub class for IOS:

.. code:: python

    # mock_device_ios.py

    import argparse

    from unicon.mock.mock_device import MockDevice

    class MockDeviceIOS(MockDevice):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


    def main(args=None):
        if not args:
            parser = argparse.ArgumentParser()
            parser.add_argument('--state', help='initial state')
            parser.add_argument('--ha', action='store_true', help='HA mode')
            parser.add_argument('--hostname', help='Device hostname (default: Router')
            args = parser.parse_args()

        if args.state:
            state = args.state
        else:
            state = 'exec,exec_standby'

        if args.hostname:
            hostname = args.hostname
        else:
            hostname = 'Router'

        if args.ha:
            md = MockDeviceTcpWrapperIOS(hostname=hostname, state=state)
            md.run()
        else:
            md = MockDeviceIOS(hostname=hostname, state=state)
            md.run()


    if __name__ == "__main__":
        main()



Running the mock device:

.. code::

    # Using device specific mock_device:

    mock_device_cli --os ios --state exec
    Router> enable
    Router#


    # Using the generic mock_device:

    mock_device_cli --os ios --state exec -generic_main
    Router> enable
    Router#



**High Availability (HA) mock device**

To create a High Availability (HA) mock device that simulates multiple RPs
or a stack of devices, you need to specify the '--ha' option with multiple 
states specified using the '--state' option, separated by a comma, for 
example:

.. code:: 

    $ mock_device_cli --os iosxr --state login,console_standby --ha
    2017-08-31 09:41:39,886 [    INFO]:  Server 0 listening on port 8266
    2017-08-31 09:41:39,888 [    INFO]:  Server 1 listening on port 8267

This will start the mock device that listens on TCP ports, one port for each RP. 

By default, the HA option creates TCP listeners. To use SSH instead of TCP,
you can use the '--ssh' option instead of '--ha'.  To run the SSH service,
the file ``ssh_host_key`` must exist with an SSH  private key in it to use
as a server host key. You can generate the file using the command
`ssh-keygen -f ssh_host_key`.

**Mock Device with vty**

To create a vty type mock device, use `--vty` option.
Currently, this is available for simplex mock device.
Supported only for TCP mock device and not require on SSH type mock device.

With `--vty` option, when we telnet to vty mock device, no need to press enter key to get the prompt.

.. code::

    $ mock_device_cli --os ios --state login --vty
    2019-02-05 12:55:19,954 [    INFO]:  Server 0 listening on port 8266

    $ telnet 127.0.0.1 8266
    Trying 127.0.0.1...
    Connected to 127.0.0.1.
    Escape character is '^]'.
    Username:

**Mock data**

The state and response data is captured in YAML files. The syntax for the mock 
data YAML file is shown below. If the prompt changes with the state, the `prompt` 
can be specified as part of the YAML data. If the prompt is shown after another
output (e.g. banner), `preface` data can be specified as a string or text block.

The filename of the YAML data is not important, all .yaml files that are part 
of the os sub directory are loaded.

To make sure that block text is correctly parsed, a block indentation indicator
may be necessary. This indicator is specified with `|n` after the node name 
where `n` is the number of indentation spaces used.

In case you want to emulate delay in responses, you can use the `timing` option 
to specify how quickly the data should be returned. Time is specified in 
seconds and can be specified as 0.01 for 10ms.

There are three timing variables that can be specified:

  * start delay
  * line interval (optional)
  * char interval (optional)

The start delay specifies the amount of time to wait before the output is 
printed to the terminal. The line interval specifies the delay between each 
line that is printed. The char interval specifies the time between characters 
of a line. The line and char interval timings are optional and can be omitted.


**Mock device data schema**

.. code:: YAML

   <state>:

     # (optional)
     preface: |2
       <text before prompt>

     # (optional)
     # preface with timing
     preface:
       response: |2
         <text before prompt>
       timing:
         # line range uses python 'slice' syntax
         # <start line>:<end line>
         # e.g. "0:"  for all lines
         - "<line range>,<start delay>,<line interval>,<char interval>"

     # (optional)
     # prompt may contain %N which will be replaced by the device hostname,
     # by default the hostname is 'Router'
     prompt: <prompt text>

     commands:
       # simple response string
       "<cmd>": ""

       # the response can be loaded from file
       # by using the `file|` prefix
       "<cmd>": file|<relative/path/to/file>

       # Multi-line response (block text)
       "<cmd>": |2
         <response data>

       # response with additional options
       "<cmd>":

         # (optional) state transition
         new_state: <state>

         # (optional) block text response
         response: |2
           <response text>

         # (optional) list of responses
         # The default behavior is to walk the list and stick to
         # the last entry when reached.
         response:
           - "abc"
           - "def"

         # (optional)
         # For list responses, you can specify response type 'circular'.
         # When circular type is enabled, the command response will
         # start again from the first entry after reaching the end of the list.
         response_type: circular

         # (optional)
         timing:
           # line range uses python 'slice' syntax
           # <start line>:<end line>
           # e.g. "0:"  for all lines
           - "<line range>,<start delay>,<line interval>,<char interval>"
           - "<line range>,<start delay>,<line interval>,<char interval>"

     keys:
       # same kind of response structure as commands
       "<key>": ""
       "<key>": |2
          <response data>

       # response with additional options
       "<cmd>":

         # (optional) state transition
         new_state: <state>

       # ... etc, see above

       # special keys: Control-X where X is one of 0ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_
       # example: ctrl-y
       "ctrl-y": "Control Y pressed"


Example data:

.. code:: YAML

    --
    exec:
      prompt: "Router> "
      commands:
        "enable":
          new_state: enable



Example: using mock device
--------------------------

Create YAML data with the state, prompt and command(s) that you want to match.


.. code:: YAML

   --
   login:
     prompt: "Username: "
     commands:
       "cisco":
         new_state: password

   password:
     prompt: "Password: "
     commands:
       "cisco":
         new_state: exec

   exec:
     prompt: "Router>"


Note: the above example data is incomplete, see 
:download:`ios_mock_data.yaml <ios_mock_data.yaml>` 
for a more complete example.


Create a unittest that executes the mock device with the state that you created. 
Execute the commands or service and verify the response data.


.. code:: python

    import unittest
    from unicon import Connection

    class TestIosPluginConnect(unittest.TestCase):

        def test_login_connect(self):
            c = Connection(hostname='Router',
                                start=['mock_device_cli --os ios --state login'],
                                os='ios',
                                username='cisco',
                                tacacs_password='cisco',
                                enable_password='cisco')
            c.connect()
            assert c.spawn.match.match_output == 'end\r\nRouter#'



Example: using HA mock device
-----------------------------



.. code:: python

    from unicon.plugins.tests.mock.mock_device_ios import MockDeviceTcpWrapperIOS


    class TestIosPluginHAConnect(unittest.TestCase):

        def setUp(self):
            self.md = MockDeviceTcpWrapperIOS(port=0, state='login,exec_standby')
            self.md.start()

            self.testbed = """
            devices:
              Router:
                os: ios
                type: router
                tacacs:
                    username: cisco
                passwords:
                    tacacs: cisco
                connections:
                  defaults:
                    class: unicon.Unicon
                  a:
                    protocol: telnet
                    ip: localhost
                    port: {}
                  b:
                    protocol: telnet
                    ip: localhost
                    port: {}
            """.format(self.md.ports[0], self.md.ports[1])

        def tearDown(self):
            self.md.stop()


        def test_connect(self):
            tb = loader.load(self.testbed)
            r = tb.devices.Router
            r.connect()
            return r

        def test_switchover(self):
            r = self.test_connect()
            r.switchover()




Known Limitations
-----------------

The current mock device has a number of limitations.

 - no support for time mocking
 - no support for random variation of response time
 - no command completion


.. sectionauthor:: Dave Wapstra <dwapstra@cisco.com>



