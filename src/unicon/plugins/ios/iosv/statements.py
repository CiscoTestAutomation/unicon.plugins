__author__ = "Myles Dear <mdear@cisco.com>"

import re


from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from .patterns import IosvPatterns


statements = GenericStatements()
patterns = IosvPatterns()


# TBD : Could use curl script to get the Pagent key
# http://wwwin-pagent.cisco.com/protected-cgi/get_key.cgi
# For now, hardcode some common machine id / Pagent keys.
PAGENT_KEYS = {
    "4294967295": "262810048832", 
    "422713650": "726452147556",
    "9": "975192883416",
}

def enter_license_handler(spawn, context):
    output = spawn.match.match_output
    match_mid = re.search(patterns.machine_id, output)
    try:
        mid = match_mid.group(1)
        try:
            spawn.sendline(PAGENT_KEYS[mid])
        except KeyError:
            raise Exception("Could not find Pagent key for Machine ID {}.".\
                format(mid))
    except Exception as exc:
        raise Exception("Could not find Pagent Machine ID for device {}.".\
            format(context.get('device_name'))) from exc


class IosvStatements():
    """
        Class that defines All the Statements for Iosv platform
        implementation
    """

    def __init__(self):
        '''
         All iosv Statements
        '''
        self.pagent_lic_stmt = Statement(
            pattern=patterns.enter_license,
            action=enter_license_handler,
            loop_continue=True,
            continue_timer=False)


