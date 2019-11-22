""" Generic IOS Settings. """

__author__ = "Sanjana Bhutani <sanbhuta@cisco.com>"

from unicon.plugins.generic.settings import GenericSettings

class IosSettings(GenericSettings):

    def __init__(self):
        super().__init__()

        self.ERROR_PATTERN = [
            r'^%\s*[Ii]nvalid (command|input)',
            r'^%\s*[Ii]ncomplete (command|input)',
            r'^%\s*[Aa]mbiguous (command|input)'
        ]

