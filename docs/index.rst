Unicon Connection Library
=========================

Unicon is a framework for developing device control libraries for routers,
switches and servers. It is developed purely in Python.

Unicon is the default connection class implementation used in Cisco pyATS 
framework. In addition, Unicon is also test framework agnostic and can be used
with/without `Cisco pyATS`_.

.. _Cisco pyATS: https://developer.cisco.com/site/pyats/

This package was initially developed internally in Cisco, and is now 
available to the general public starting late 2017 through `Cisco DevNet`_. 

``unicon.plugins`` is plugins for different platforms. All the platform
implementations are arranged in a hierarchical fashion in order  to provide
a good fault isolation.

    https://developer.cisco.com/site/pyats/
    
.. _Cisco DevNet: https://developer.cisco.com/

--------------------------------------------------------------------------------

User Guide
----------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/introduction
   user_guide/supported_platforms
   user_guide/services/index
   user_guide/services/service_dialogs

Developer Guide
---------------

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide

   developer_guide/plugins
   developer_guide/unittests

Change Log
----------

.. toctree::
   :maxdepth: 2
   :caption: Resources

   changelog/index

.. sectionauthor:: ATS Team
