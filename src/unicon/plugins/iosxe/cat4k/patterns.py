from unicon.plugins.iosxe.patterns import IosXEPatterns

class IosXECat4kPatterns(IosXEPatterns):
    def __init__(self):
        super().__init__()
        self.restart = r'^(.*)estarting system(.*)'
