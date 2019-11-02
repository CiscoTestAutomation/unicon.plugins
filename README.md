[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoTestAutomation/unicon_plugins)

# Unicon

Unicon is a framework for developing device control libraries for routers,
switches and servers. It is developed purely in python, hence no dependency on
Tcl based infrastructure. Unicon is also test framework agnostic and can be used
with/without pyats.

As a framework it provides a set of classes and settings which can be
further sub-classed to create platform specific implementations.

One of the main design goals of unicon is `DRY` (Do Not Repeat Yourself).
Hence the base classes handle all the common stuff which are applicable to all
the platforms. This makes it very easy for a developer to implement connection
library for a targeted platform, as she only ends up writing the differential
code.

The unicon_plugins package provides built-in plugins for a variety of platforms.
All the platform implementations are arranged in a hierarchical fashion in order 
to provide a good fault isolation. It was initially developed internally in Cisco, 
and is now available to the general public starting late 2017 through [Cisco DevNet].

[Cisco DevNet]: https://developer.cisco.com/

# Installation

Installation guide can be found on [our website].

[our website]: https://developer.cisco.com/site/pyats/

```
$ pip install unicon
$ pip install unicon_plugins
```

# ChangeLog

Change logs can be found [here](docs/changelog).

> Copyright (c) 2019 Cisco Systems, Inc. and/or its affiliates