__author__ = "Myles Dear <mdear@cisco.com>"

import re


from unicon.eal.dialogs import Statement
from unicon.plugins.generic.patterns import GenericPatterns

patterns = GenericPatterns()

def enter_license_handler(spawn, context):
    mid = ''
    m = re.search(r'Machine ID: (?P<mid>\d+)', spawn.match.match_output)
    if m:
        mid = m['mid']
    try:
        spawn.sendline(context['pagent_key'])
        spawn.expect(r'.*is valid.*done')
        spawn.expect(r'.*> *$')
        spawn.sendline('enable')
    except KeyError:
        raise Exception("Could not find Pagent key for Machine ID {}.".\
            format(mid))


class IosPagentStatements():
    """
        Class that defines All the Statements for Pagent platform
        implementation
    """

    def __init__(self):
        '''
         All pagent Statements
        '''
        self.pagent_lic_stmt = Statement(
            pattern=patterns.enter_license,
            action=enter_license_handler,
            loop_continue=True,
            continue_timer=False)



