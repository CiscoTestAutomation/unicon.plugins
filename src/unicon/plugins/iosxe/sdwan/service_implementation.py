
from unicon.plugins.iosxe.service_implementation import Configure

class SDWANConfigure(Configure):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.commit_cmd = "commit"
