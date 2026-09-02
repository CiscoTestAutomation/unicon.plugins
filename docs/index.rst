Unicon: The Connection Library
==============================

Unicon is a package aiming to provide a unified connection experience to network
devices through typical command-line management interface. By wrapping the 
underlying session (eg, telnet, ssh), Unicon provides:

- direct and proxied connections through any common CLI interface (telnet, ssh, serial etc)
- power of expect-like programming without having to deal with low-level logic
- multi-vendor support through an agnostic API interface
- seamless handling of CLI modes (eg, enable, configure, admin-configure mode)
- rejected commands, command error detections
- value-add stateful services (specific to the platform)

and is extensible: platform supports and services are implemented via 
open-source plugins.

Unicon is the standard, go-to CLI connection implementation for `Cisco pyATS`_
framework.

.. _Cisco pyATS: https://developer.cisco.com/site/pyats/

This package was initially developed internally in Cisco, and is now 
released to the general public starting late 2017 through `Cisco DevNet`_.

    https://developer.cisco.com/pyats/
    
.. _Cisco DevNet: https://developer.cisco.com/

--------------------------------------------------------------------------------

.. toctree::
    :maxdepth: 2
    :caption: User Guide

    user_guide/introduction
    user_guide/supported_platforms
    user_guide/connection
    user_guide/passwords
    user_guide/proxy
    user_guide/services/index
    user_guide/services/service_dialogs
    robot/index

.. toctree::
    :maxdepth: 2
    :caption: Developer Guide

    playback/index
    developer_guide/plugins
    developer_guide/service_framework
    developer_guide/eal
    developer_guide/statemachine
    developer_guide/unittests


.. toctree::
    :maxdepth: 2
    :caption: Resources

    api/modules
    changelog/index
    changelog_plugins/index

.. sectionauthor:: ATS Team
