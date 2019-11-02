What Are Services
=================

Services are API's to perform general administrative tasks on the devices in a
platform agnostic manner. We also use the word `subcommands` interchangably to
refer to services. Both mean the same.

These APIs or their usage do not change from platform to platform and provide
a uniform software view of the device. But it is possible that few services
are only applicable on a particular platform. For example, services for VDC
handling will only be available for NXOS. Few services like `switchover` are
only relevant on HA devices.

Common tasks we perform on routers are executing a command, configuring the
device by issuing commands in config mode, ping, reload, switchover etc.
These commands may vary in behaviour or the options, but if you use services
for performing these operations then the same code could be executed on any
platform without worrying about the exact command specifications applicable
on that platform.

Whenever you have to perform any operation on the device, first check whether
there is a service already available for the same. If no services are available
then you can use lower interaction APIs like `send`, `sendline` and `expect`.
