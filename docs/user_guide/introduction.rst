Introduction
============

Unicon is a framework for developing device control libraries for routers,
switches and servers. It is developed purely in Python. 

One of the main design goals of Unicon is **D.R.Y.** (Do not Repeat Yourself).
Hence, to avoid the nuisance/boiler-plate code copy/pasted everywhere, the 
infrastructure is broken down into implementation tiers, where the higher ups
handles common stuff which are applicable to all platforms, and the lower 
implementation details are specific to target devices - eg, developers will be
required to only implement what's different between devices/platforms.

Unicon is broken down into two components:

Core
    the core of Unicon is developed and maintained by Cisco DevX engineering
    team. It focuses on things such as dialog processing, state-machine
    flow, pattern matchers, buffer and generic terminal handling. 
    This comes in the form of ``unicon`` PyPI package.

Plugins
    all specific platform details, services and command-line patterns are 
    implemented in this open-source plugin layer, the ``unicon.plugins`` package.


Installation
------------

Though Unicon is broken down into two separate packages:

- ``unicon``: the core framework
- ``unicon.plugins``: plugins and libraries

the whole solution can be installed using ``pip`` all in one shot:

.. code-block:: bash

    bash$ pip install unicon

You can however, upgrade individual packages if you wish:

.. code-block:: bash

    bash$ pip install --upgrade unicon
    bash$ pip install --upgrade unicon.plugins


Support & Community
-------------------

See https://developer.cisco.com/docs/pyats/#!license-support page for details.
