"""
Module:
    unicon.plugins.hvrp

Authors:
    Miguel Botia (mibotiaf@cisco.com), Leonardo Anez (leoanez@cisco.com)

Description:
    Module for defining all the Patterns required for the HVRP implementation.
"""

from unicon.patterns import UniconCorePatterns


class HvrpPatterns(UniconCorePatterns):

    """
        Class defines all the patterns required
        for Hvrp
    """
    def __init__(self):
        super().__init__()
        self.username = r'^.*[Ll]ogin:$'
        self.password = r'^.*[Pp]assword:$'
        
        # <HOSTNAME> #
        self.enable_prompt = r'^(.*)\<\w+\>$'

        # [~HOSTNAME] #
        self.config_prompt = r'^(.*)\[\~*\S+\]$'

        # Exit with uncommitted changes? [yes,no] (yes)
        self.commit_changes_prompt = r'Exit with uncommitted changes?'
        self.password_ok = r'Password OK\s*$'

        # Bad Password
        self.bad_passwords = r'Permission denied.*'
