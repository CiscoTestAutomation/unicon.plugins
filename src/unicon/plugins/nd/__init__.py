"""
Module:
    unicon.plugins.nd

Authors:
    pyATS TEAM (pyats-support-ext@cisco.com)

Description:
    This subpackage implements ND
"""

from unicon.plugins.linux import LinuxConnection


class NDConnection(LinuxConnection):
    """
    Connection class for ND connections.
    Extends the Linux connection to function with 'nd' os.
    """
    os = 'nd'
