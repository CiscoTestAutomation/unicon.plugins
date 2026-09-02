from unicon.plugins.ise.patterns import IsePatterns
from unicon.plugins.generic.service_implementation import \
    Configure as GenericConfigure, \
    Execute as GenericExecute


class Execute(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'shell'
        self.end_state = 'shell'


class Configure(GenericConfigure):

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'config'
        self.end_state = 'shell'
