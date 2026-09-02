__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.statemachine import State, Path, StateMachine

from .patterns import SrosPatterns

patterns = SrosPatterns()


class SrosSingleRpStateMachine(StateMachine):

    def create(self):
        mdcli = State('mdcli', patterns.mdcli_prompt)
        classiccli = State('classiccli', patterns.classiccli_prompt)

        mdcli_to_classiccli = Path(mdcli, classiccli, '//')
        classiccli_to_mdcli = Path(classiccli, mdcli, '//')

        self.add_state(mdcli)
        self.add_state(classiccli)

        self.add_path(mdcli_to_classiccli)
        self.add_path(classiccli_to_mdcli)
