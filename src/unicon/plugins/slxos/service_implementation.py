"""
Module:
    unicon.plugins.slxos
Authors:
    Fabio Pessoa Nunes (https://www.linkedin.com/in/fpessoanunes/)
Description:
    This subpackage implements services specific to Slxos.
"""

from unicon.plugins.generic.service_implementation import Send, Sendline, \
                                                          Expect, Execute, \
                                                          Configure, Copy
from unicon.eal.dialogs import Dialog
from unicon.plugins.slxos.patterns import SlxosPatterns
from unicon.plugins.slxos.statements import slxos_statements


class Copy(Copy):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.dialog += Dialog([slxos_statements.save_confirm])


class Save(Copy):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def call_service(self):
        super().call_service(source='running-config', dest='startup-config')
