Introduction
============

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

All the platform implementations are arranged in a hierarchical fashion in order
to provide a good fault isolation. We will talk about more on framework details
in next iteration of documentation update, which will follow shortly.

``unicon.plugins`` is plugins for different platforms.

Installation
------------

unicon and unicon.plugins can be installed using the `pip` command. Assuming
that you have already sourced your virtualenv, run the following commands
on the shell::

    pip install unicon
    pip install unicon.plugins

Community
---------

Feel free to join us by visiting our DevNet portal at
https://developer.cisco.com/site/pyats/.
