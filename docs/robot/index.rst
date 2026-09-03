RobotFramework Support
======================

.. sidebar:: Quick References

    - `RobotFramework`_
    - `Unicon Keywords`_

.. _RobotFramework: http://robotframework.org/
.. _Unicon Keywords: ../robot.html

Robot Framework is generic Python/Java test automation framework that focuses
on acceptance test automation by through English-like keyword-driven test
approach.

Starting Unicon v3.1.0, Robot Framework support has been added through the
optional ``robot`` sub-package under `Unicon.robot` namespace umbrella. This enables 
RobotFramework users to leverage key aspects of Genie without having to reinvent
the wheel. Robot Framework libraries have also been added for pyATS and Genie.

Installation
------------

Robot Framework support is an optional component under Unicon. To use it, you 
must install this package explicitly:

.. code-block:: bash

    pip install unicon[robot]


Features
--------

- Execute command on device
- Configure command on device
- Enable/Disable device output
- Set Unicon settings

Keywords
--------

For the complete set of keywords supported by this package, refer to
`Unicon Keywords`_.

Example
-------

.. code-block:: robotframework
    
    # Example
    # -------
    # 
    #   Demonstration of Unicon Robot Framework Keywords

    *** Settings ***
    Library    ats.robot.pyATSRobot
    Library    unicon.robot.UniconRobot
    
    *** Test Cases ***

    Connect to device
        use testbed "testbed.yaml"
        # Remove default connection commands
        set unicon setting "HA_INIT_CONFIG_COMMANDS" "" on device "nx-osv-1"
        connect to device "uut"
    
    Execute command
        execute "show devices list" on device "uut"
        configure "router bgp 100" on device "uut"
    
    Execute command in parallel on multiple devices
        execute "show devices list" in parallel on devices "uut"
    
    Disconnect from device
        disconnect from device "uut"
