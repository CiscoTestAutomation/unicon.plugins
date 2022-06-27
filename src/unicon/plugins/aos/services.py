'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
import logging

from unicon.plugins.generic.service_implementation import Execute as GenericExec
from unicon.plugins.ios.iosv import IosvServiceList
from unicon.plugins.generic import ServiceList, service_implementation as aosSi
from unicon.plugins.junos import service_implementation as svc
from unicon.plugins.aos.connection_provider import aosSingleRpConnectionProvider

class aosServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.execute = svc.Execute
        self.configure = svc.Configure
        self.enable = svc.Enable
        self.disable = svc.Disable
        self.log_user = svc.LogUser
        self.bash_console = svc.BashService
        self.expect_log = aosSi.ExpectLogging
        self.run_command = aosSingleRpConnectionProvider

