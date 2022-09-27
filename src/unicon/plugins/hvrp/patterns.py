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
        self.username = r'^.*[Ll]ogin:'
        self.password = r'^.*[Pp]assword:'

        # <HOSTNAME-01> | <HOSTNAME>#
        self.enable_prompt = r'^(.*)\<%N.*\>$'


        # [~HOSTNAME] | <HOSTNAME-01> # # breaks on [\y\n] # Warning: All the configuration will be saved to the next startup configuration. Continue? [y/n]:
        self.config_prompt = r'^.*\[(~|\*)%N.*\]'

        # Exit with uncommitted changes? [yes,no] (yes)
        self.commit_changes_prompt = r'Exit with uncommitted changes? [yes,no] (yes)\s*'

        self.save_prompt = r'^(.*)Warning: All the configuration will be saved to the next startup configuration. Continue\? \[y\/n\]:'

        self.reboot_prompt = r'^(.*)System will reboot! Continue\? \[y\/n\]:'

        # Correct Password
        self.password_ok = r'Password OK\s*'

        # Bad Password
        self.bad_passwords = r'Permission denied.*'
