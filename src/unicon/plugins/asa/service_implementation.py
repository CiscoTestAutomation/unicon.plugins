import os
import re

from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.service_implementation import Execute as GenericExecute, \
    Reload as GenericReload

from .patterns import (ASAPatterns)
from .statements import execute_statements, reload_statements

class ASAExecute(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog(execute_statements)

class ASAReload(GenericReload):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog(reload_statements)