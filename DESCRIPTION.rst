Unicon Plugins
==============

.. note::

    this is the plugins component of Unicon. The usage of this package requires
    ``unicon`` main package.

Unicon is a package aiming to provide a unified connection experience to network
devices through typical command-line management interface. By wrapping the 
underlying session (eg, telnet, ssh), Unicon provides:

- direct and proxied connections through any common CLI interface (telnet, ssh, serial etc)
- power of expect-like programming without having to deal with low-level logic
- multi-vendor support through an agnostic API interface
- seamless handling of CLI modes (eg, enable, configure, admin-configure mode)
- rejected commands, command error detections
- value-add statful services (specific to the platform)

and is extensible: platform supports and services are implemented via 
open-source plugins.

Unicon is the standard, go-to CLI connection implementation for `Cisco pyATS`_
framework.

.. _Cisco pyATS: https://developer.cisco.com/site/pyats/

This package was initially developed internally in Cisco, and is now 
release to the general public starting late 2017 through `Cisco DevNet`_. 

    https://developer.cisco.com/pyats/
    
.. _Cisco DevNet: https://developer.cisco.com/


Requirements
------------

- Linux/macOS/WSL
- Python 3.4+

Quick Start
-----------

.. code-block:: bash

    bash$ pip install unicon


For more information on setting up your Python development environment,
such as creating virtual environment and installing ``pip`` on your system, 
please refer to `Virtual Environment and Packages`_ in Python tutorials.

.. _Virtual Environment and Packages: https://docs.python.org/3/tutorial/venv.html

Examples
--------

See example of a Unicon connection usage with Cisco IOS devices at:

    https://github.com/CiscoDevNet/pyats-ios-sample

In addition, there is a sample plugin package you can follow to develop Unicon
plugins for new platforms on top of Unicon:

    https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example

Support & Community
-------------------

See https://developer.cisco.com/docs/pyats/#!license-support page for details.
