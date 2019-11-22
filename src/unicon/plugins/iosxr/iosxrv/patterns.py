from unicon.plugins.iosxr.patterns import IOSXRPatterns

class IOSXRVPatterns(IOSXRPatterns):
    def __init__(self):
        super().__init__()
        self.xr_admin_prompt = r'(^.*?)RP/\S+\(admin\)#\s?$'


