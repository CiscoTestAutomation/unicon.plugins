'''
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from .patterns import GaiaPatterns
from unicon.utils import to_plaintext
from time import sleep

statements = GenericStatements()
patterns = GaiaPatterns()


def expert_password_handler(spawn, context, session):
    credentials = context.get('credentials')
    expert_credential_password = credentials.get('expert', {}).get('password')

    expert_password = to_plaintext(expert_credential_password)
    sleep(0.1)
    spawn.sendline(expert_password)
    sleep(0.1)
    spawn.sendline()


class GaiaStatements(GenericStatements):
    """
        Class that defines the Statements for Gaia plugin
        implementation
    """

    def __init__(self):
        super().__init__()

        self.expert_password_stmt = Statement(
            pattern=patterns.expert_password_prompt,
            action=expert_password_handler,
            args=None,
            loop_continue=True,
            continue_timer=False)
