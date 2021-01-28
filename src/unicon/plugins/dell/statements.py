'''
Author: Knox Hutchinson
Contact: https://dataknox.dev
https://twitter.com/data_knox
https://youtube.com/c/dataknox
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from .patterns import DellPatterns 
from unicon.bases.routers.connection import ENABLE_CRED_NAME
from unicon.utils import to_plaintext
from unicon.core.errors import UniconAuthenticationError

statements = GenericStatements()
patterns = DellPatterns()

def login_handler(spawn, context, session):
    spawn.sendline(context['enable_password'])

def send_enabler(spawn, context, session):
    spawn.sendline('enable')


def confirm_imaginary_handler(spawn):
    spawn.sendline('i concur')

def get_enable_credential_password(context):
    credentials = context.get('credentials')
    enable_credential_password = ""
    login_creds = context.get('login_creds', [])
    fallback_cred = context.get('default_cred_name', "")
    if not login_creds:
        login_creds=[fallback_cred]
    if not isinstance (login_creds, list):
        login_creds = [login_creds]

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


