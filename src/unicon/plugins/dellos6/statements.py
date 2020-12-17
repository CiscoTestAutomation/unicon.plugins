'''
Connection Statements
---------------------
Automation is all about automatically performing actions without human 
intervention. This includes automatically answering to dialog prompts by 
programmatically replying to each dialog prompt.
Statements are the building blocks of dialog handling logic within Unicon.
Typically Unicon plugins have a statements.py file where all statements 
particular to this platform is located.
'''
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from .patterns import DellosPatterns 
from unicon.bases.routers.connection import ENABLE_CRED_NAME
from unicon.utils import to_plaintext
# handlers are necessary actions to take (functions)
# when a particular statement is met

statements = GenericStatements()
patterns = DellosPatterns()

def login_handler(spawn, context, session):
    spawn.sendline(context['enable_password'])

def send_enabler(spawn, context, session):
    spawn.sendline('enable')


def confirm_imaginary_handler(spawn):
    spawn.sendline('i concur')

def get_enable_credential_password(context):
    """ Get the enable password from the credentials.

    1. If there is a previous credential (the last credential used to respond to
       a password prompt), use its enable_password member if it exists.
    2. Otherwise, if the user specified a list of credentials, pick the final one in the list and
       use its enable_password member if it exists.
    3. Otherwise, if there is a default credential, use its enable_password member if it exists.
    4. Otherwise, use the well known "enable" credential, password member if it exists.
    5. Otherwise, use the default credential "password" member if it exists.
    6. Otherwise, raise error that no enable password could be found.

    """
    credentials = context.get('credentials')
    enable_credential_password = ""
    login_creds = context.get('login_creds', [])
    fallback_cred = context.get('default_cred_name', "")
    if not login_creds:
        login_creds=[fallback_cred]
    if not isinstance (login_creds, list):
        login_creds = [login_creds]

    # Pick the last item in the login_creds list to select the intended
    # credential even if the device does not ask for a password on login
    # and the given credential is not consumed.
    final_credential = login_creds[-1] if login_creds else ""
    if credentials:
        enable_pw_checks = [
            (context.get('previous_credential', ""), 'enable_password'),
            (final_credential, 'enable_password'),
            (fallback_cred, 'enable_password'),
            (ENABLE_CRED_NAME, 'password'),
            (context.get('default_cred_name', ""), 'password'),
        ]
        for cred_name, key in enable_pw_checks:
            if cred_name:
                candidate_enable_pw = credentials.get(cred_name, {}).get(key)
                if candidate_enable_pw:
                    enable_credential_password = candidate_enable_pw
                    break
        else:
            raise UniconAuthenticationError('{}: Could not find an enable credential.'.\
                format(context.get('hostname', "")))
    return to_plaintext(enable_credential_password)


def enable_password_handler(spawn, context, session):
    if 'password_attempts' not in session:
        session['password_attempts'] = 1
    else:
        session['password_attempts'] += 1
    if session.password_attempts > spawn.settings.PASSWORD_ATTEMPTS:
        raise UniconAuthenticationError('Too many enable password retries')

    enable_credential_password = get_enable_credential_password(context=context)
    if enable_credential_password:
        spawn.sendline(enable_credential_password)
    else:
        spawn.sendline(context['enable_password'])


# define the list of statements particular to this platform
login_stmt = Statement(pattern=patterns.login_prompt,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=False)

enable_stmt = Statement(pattern=patterns.disable_mode,
                        action=send_enabler,
                        args=None,
                        loop_continue=True,
                        continue_timer=False)


password_stmt = Statement(pattern=patterns.password,
                        action=enable_password_handler,
                        args=None,
                        loop_continue=True,
                        continue_timer=False)

# confirm_imaginary_platform = Statement(pattern=patterns.confirm_imaginary,
#                                        action=confirm_imaginary_handler,
#                                        args=None,
#                                        loop_continue=True,
#                                        continue_timer=False)
