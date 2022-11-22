.. _new-service-creation:

How to write  a new Service
============================

Let us divide this task into 3 topics.

  1. Steps involved in service implementation.
  2. Writing a sample service.
  3. How to attach a service to connection object.

Steps involved in service implementation
-----------------------------------------

We shall divide this implementation into 4 steps steps, which includes.

1. What are pre-requisites I need to take care before running the service.
we call it as **'pre_service'**. One of them will be if connection is established,
before try to execute a service on the connection. Change the state of the device
to initial state for the service to be in.

Before start coding pre_service, let us go through __init__ of BaseService Class.
  * *connection* : Device connection object

  * *context* : Context info from user (more details we can get it from connection class)

  * *timeout_pattern* : Will have list of timeout patterns, I would like to match in device response after service execution.

  * *error_pattern*  : Will have list of error patterns, I would like to match in device response after service execution.

  * *start_state* : Which state, device should be in before executing the service.

  * *end_state* : Which state, device should be after executing the service.

  * *result* : result attribute will have return response from device after service execution. Which will be used to evaluate the service result.

.. code-block:: python

  def __init__(self,  connection,  context, **kwargs):
    self.connection = connection
    self.context = context
    self.timeout_pattern = ['Timeout occurred', ]
    self.error_pattern = ["my command error"]
    self.start_state = 'enable'
    self.end_state = 'enable'
    self.result = None
    self.__dict__.update(kwargs)


  def pre_service(self, *args, **kwargs):
    # Check if connection is established. If reconnect option is enabled
    # then reconnect and execute the command, or raise error.

    if self.connection.is_connected:
        return
    elif self.connection.reconnect:
        self.connection.connect()
    else:
        raise ConnectionError("Connection is not established to device")

    # Bring the device to required state to issue a command.

    self.connection.state_machine.go_to(self.start_state,
                                        self.connection.spawn,
                                        context=self.connection.context)




2. Actual service implementation goes here, we call it **'call_service'**.

.. code-block:: python

  def call_service(self, command, dialog=Dialog([]) *args, **kwargs):
       # Command to issue on device is `command`
       con = self.connection
       con.log.debug("+++ run_command +++ ")
       con.spawn.sendline(command)
       # self.result attribute will be used at result validation.
       self.result = con.spawn.expect(.*#?)


.. note::

    Any input object sent by the user calling your service, if not passed
    directly to the ``send`` or ``sendline`` spawn method, must be properly
    converted to a string form.  Users are allowed to specify non-string
    objects as input.

    Also, if your service accepts lists of objects, make sure you also
    accept list-like objects that are instances of collections.Sequence.


3. **'post_service'**  includes reverting the device to earlier state. One of
them will be bringing the device to end state of that service after service execution.
for example after reload service device must be in enable state.

.. code-block:: python

  def post_service(self, *args, **kwargs):
    # Bring the device back to end state.
    self.connection.state_machine.go_to(self.end_state,
                                        self.connection.spawn,
                                        context=self.connection.context)

4. Final step will be **'get_service_result'** will verify the self.result (response of each service)
with service error_pattern and timeout_pattern. If self.result doesn't match
any of the above pattern, service result will be considered pass or it
raises SubCommandFailure exception.

.. code-block:: python

  def get_service_result(self):
    #  return True is self.result has <xyz> string in it or raise exception.

    if re.search("xvy", self.result):
      self.result = True
      return self.result
    else :
        raise SubcommandFailure("xyz is not found in device response")


Writing a sample service
------------------------

For example I wanted to implement a service which issue given command  in
*enable* mode and device and get the return response from device. Then return
the device back in *disable* mode.

Also, if the command we are trying to run will prompt a dialog/take additional
input, Use **'Dialog'** (list of Statements) which are expected to prompt.


.. code-block:: python

  # Import BaseService

    from unicon.bases.routers.services import BaseService
    from unicon.eal.dialogs import Dialog


    class RunCommand(BaseService):
      def __init__(self,  connection,  context, **kwargs):
          self.connection = connection
          self.context = context
          self.timeout_pattern = ['Timeout', "Timed Out" ]
          self.error_pattern = ["error", "abort"]
          self.start_state = 'enable'
          self.end_state = 'disable'
          self.result = None
          self.__dict__.update(kwargs)

      def pre_service(self, *args, **kwargs):
          # Check if connection is established
          if self.connection.is_connected:
              return
          elif self.connection.reconnect:
              self.connection.connect()
          else:
              raise ConnectionError("Connection is not established to device")

          # Bring the device to required state to issue a command.
          self.connection.state_machine.go_to(self.start_state,
                                              self.connection.spawn,
                                              context=self.connection.context)

      def call_service(self, command,
                       dialog=Dialog([]),
                       timeout=20,
                       *args, **kwargs):
          # Command to issue on device is `command`
          con = self.connection
          con.log.debug("+++ run_command +++ ")
          if dialog is None:
            # Run command
            con.spawn.sendline(command)
            # self.result attribute will be used at result validation.
            self.result = con.spawn.expect(.*#?)
          else:
            self.result = dialog.process(con.spawn, timeout=timeout)


      def post_service(self, *args, **kwargs):
          # Bring the device back to end state which is disable
          self.connection.state_machine.go_to(self.end_state,
                                              self.connection.spawn,
                                              context=self.connection.context)

      def get_service_result(self):
          # Base class get_service will verify error and timeout pattern and return
          # self.result content if no error found.
          pass


How to attach a service to connection object
--------------------------------------------
Make an entry in the service list and pass on the service list to Connection class.

.. code-block:: python

  from unicon.plugins.generic.services import ServiceList, HAServiceList
   from .*. import implementation RunCommand

  class NxosServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        # Add the command defined to existing service list
        self.run_command = RunCommand

  class NXOSConnection(BaseDualRpConnection):
        os = 'nxos'
        platform = None
        chassis_type = 'dual_rp
        state_machine_class = IosDualRpStateMachine
        connection_provider_class = IosDualRpConnectionProvider
        subcommand_list = NxosServiceList ; < update subcommand_list with new list defined
        settings = IosConnectionSettings()

Implementing prompt_recovery feature in service
-----------------------------------------------
To add prompt_recovery feature in plugin service, plugin developers can use prompt_recovery argument with `Dialog.process()` and `go_to()`.
`prompt_recovery` attribute for the service is set at the time of `pre_service` function.
If `pre_service` is implemented as part of service implementation then `super()` need to use in `pre_service`.

**Prompt recovery configuration**

Prompt recovery can configure using below three settings:

    * PROMPT_RECOVERY_COMMANDS : List of command which need to send after normal dialog timeout. It should be a list. Plugin developers can set or append values. New commands can be appended to `PROMPT_RECOVERY_COMMANDS` or can be overwritten with new value.
    * PROMPT_RECOVERY_INTERVAL : Timeout period after sending each prompt recovery command, in secs. Type is int. Default value: 10 secs
    * PROMPT_RECOVERY_RETRIES  : Number of prompt recovery retires to perform. Type is int. Default value: 1

These settings should go in plugin settings file, so that platform specific values utilize.
