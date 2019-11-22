
from time import sleep

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements

from .patterns import VosPatterns

p = VosPatterns()


def paginate(spawn, context, session):
    """ paginating """
    m = spawn.match.last_match
    begin_page_line = m.group(1)
    end_page_line = m.group(2)
    total_lines = m.group(3)

    if (end_page_line == total_lines) or (int(end_page_line) >= context.get('lines', 100)):
      spawn.send('q')
    else:
      spawn.send('n')

def press_space(spawn):
    sleep(.02)
    spawn.send(' ')


class VosStatements(GenericStatements):
    """
        Class that defines the Statements for CIMC platform
        implementation
    """

    def __init__(self):
        '''
         All CIMC Statements
        '''
        super().__init__()

        self.paginate_stmt = \
            Statement(pattern=p.paging_options,
              action=paginate,
              args=None,
              loop_continue=True,
              continue_timer=True)

        self.press_enter_space_q_stmt = \
            Statement(pattern=p.press_enter_space_q,
                      action=press_space,
                      args=None,
                      loop_continue=True,
                      continue_timer=True)

        self.continue_stmt = \
            Statement(pattern=p.continue_prompt,
              action='sendline(y)',
              args=None,
              loop_continue=True,
              continue_timer=True)


statements = VosStatements()

vos_default_statement_list = [
    statements.press_enter_space_q_stmt,
    statements.paginate_stmt,
]

