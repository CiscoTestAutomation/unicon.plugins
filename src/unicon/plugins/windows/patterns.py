__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns

class WindowsPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.prompt = r'^(.*?)\S+@%N\s+.*?>\s*(\x1b.*)?$'
