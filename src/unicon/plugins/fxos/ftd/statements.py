__author__ = "dwapstra"

from unicon.eal.dialogs import Statement

from .patterns import FtdPatterns


patterns = FtdPatterns()


def flag_ssh_session(spawn, context, session):
    context._ssh_session = True
    spawn.log.info('SSH session detected')


def clear_command_line(spawn, context, session):
    """ Clear the command line by sending Ctr-A Ctrl-K """
    CTRL_A = '\x01'
    CTRL_K = '\x0b'
    spawn.sendline("%s%s" % (CTRL_A, CTRL_K))


class FtdStatements(object):

    def __init__(self):
        '''
         All FTD Statements
        '''
        self.cssp_stmt = Statement(patterns.cssp_pattern,
                                   action=flag_ssh_session,
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=False)

        self.command_not_completed_stmt = Statement(patterns.command_not_completed,
                                   action=clear_command_line,
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=False)

        self.are_you_sure_stmt = Statement(patterns.are_you_sure,
                                  action='sendline(y)',
                                  args=None,
                                  loop_continue=True,
                                  continue_timer=False)