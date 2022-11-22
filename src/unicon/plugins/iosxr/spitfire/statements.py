from unicon.plugins.generic.statements import GenericStatements, pre_connection_statement_list
from unicon.plugins.iosxr.spitfire.patterns import SpitfirePatterns
from unicon.eal.dialogs import Statement

from unicon.plugins.utils import (
    get_current_credential,
    common_cred_username_handler,
    common_cred_password_handler,
)

patterns = SpitfirePatterns()

BMC_CRED = 'bmc'


def password_handler(spawn, context, session, reuse_current_credential=False):
    """ handles password prompt
    """
    if session.get('bmc_login') == 1:
        credential = BMC_CRED
        # BMC login automatically uses a specific named credential and doesn't
        # use credentials from the login_creds list.
        reuse_current_credential = True
    else:
        credential = get_current_credential(context=context, session=session)

    if credential:
        common_cred_password_handler(spawn=spawn,
                                     context=context,
                                     credential=credential,
                                     session=session,
                                     reuse_current_credential=reuse_current_credential)
    else:
        if session.get('enable_login') == 1:
            spawn.sendline(context['enable_password'])
        elif session.get('bmc_login') == 1:
            spawn.sendline(context['bmc_password'])
        else:
            spawn.sendline(context['xr_password'])
            # if this password fails, try with tacacs password
            session['tacacs_login'] = 1


def xr_login_handler(spawn, context, session):
    """ handles xr login prompt
    """
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_username_handler(spawn=spawn, context=context, credential=credential)
    else:
        spawn.sendline(context['username'])
        session['enable_login'] = 1


def bmc_login_handler(spawn, context, session):
    """ handles bmc login prompt
    """
    credential = BMC_CRED
    session['bmc_login'] = 1
    if credential:
        common_cred_username_handler(spawn=spawn, context=context, credential=credential)
    else:
        spawn.sendline(context['bmc_username'])


class SpitfireStatements(GenericStatements):
    def __init__(self):
        super().__init__()

        self.login_stmt = Statement(pattern=patterns.username_prompt,
                                    action=xr_login_handler,
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=False)

        self.bmc_login_stmt = Statement(pattern=patterns.bmc_login_prompt,
                                        action=bmc_login_handler,
                                        args=None,
                                        loop_continue=True,
                                        continue_timer=False)

        self.password_stmt = Statement(pattern=patterns.password_prompt,
                                       action=password_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)

        self.secret_password_stmt = Statement(pattern=patterns.secret_password_prompt,
                                              action=password_handler,
                                              args={'reuse_current_credential': True},
                                              loop_continue=True,
                                              continue_timer=False)


spitfire_statements = SpitfireStatements()

#############################################################
# Authentication Statement
#############################################################

authentication_statement_list = [
    spitfire_statements.bad_password_stmt,
    spitfire_statements.login_incorrect,
    spitfire_statements.bmc_login_stmt,
    spitfire_statements.login_stmt,
    spitfire_statements.useraccess_stmt,
    spitfire_statements.password_stmt,
    spitfire_statements.secret_password_stmt,
]

connection_statement_list = authentication_statement_list + pre_connection_statement_list
