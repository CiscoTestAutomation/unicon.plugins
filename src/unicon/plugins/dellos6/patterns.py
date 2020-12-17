'''
Unicon Plugin Patterns
----------------------
Pattern module in a Unicon plugin allows developers to consolidate all
regex patterns that matches dialogs, statements & the likes into one location.
'''
import re

from unicon.plugins.generic.patterns import GenericPatterns


class DellosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.login_prompt = r' *login here: *?'
        self.disable_mode = r'\w+>$'
        self.privileged_mode = r'\w+[^\(config\)]#$'
        self.config_mode = r'\w+\(config[-\w]+\)#$'
        self.password = r'Password:'
