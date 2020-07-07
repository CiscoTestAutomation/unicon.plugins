"""
Module:
    unicon.plugins.junos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This subpackage implements Junos devices
"""
from unicon.plugins.junos import JunosSingleRpConnection
from .statemachine import JunosVsrxSingleRpStateMachine


class JunosVsrxSingleRpConnection(JunosSingleRpConnection):
    os = 'junos'
    series = 'vsrx'
    chassis_type = 'single_rp'
    state_machine_class = JunosVsrxSingleRpStateMachine
