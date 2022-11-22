"""
Module:
    unicon.plugins.junos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining all the Patterns required for the
    Junos implementation
"""
from unicon.patterns import UniconCorePatterns


class JunosPatterns(UniconCorePatterns):

    """
        Class defines all the patterns required
        for Junos
    """
    def __init__(self):
        super().__init__()
        self.username = r'^.*[Ll]ogin: ?$'
        self.password = r'^.*[Pp]assword: ?$'
        
        # root@junos_vmx1:~ # 
        self.shell_prompt = r'^(.*)?(%N)(-RE[01])?\:\~ *\#\s?$|^%\s*$'

        # root@junos_vmx1>
        self.enable_prompt = r'^(.*?)([-\.\w]+@(%N)+(-RE[01])?>)\s*$'

        # root@junos_vmx1:~ # 
        self.disable_prompt = r'^(.*)?(%N)(-RE[01])?\:\~ *\#\s?$'

        # root@junos_vmx1#
        self.config_prompt = r'^(.*?)([-\.\w]+@(%N)+(-RE[01])?[\%\#])\s*$'

        # Exit with uncommitted changes? [yes,no] (yes)
        self.commit_changes_prompt = r'Exit with uncommitted changes?'
        self.password_ok = r'Password OK\s*$'
