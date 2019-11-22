import time
from unicon.eal.dialogs import Statement
from unicon.eal.helpers import sendline

from .patterns import ASAPatterns
from .settings import ASASettings

from unicon.plugins.generic.statements import (
    connection_failure_handler,
    connection_refused_handler,
    bad_password_handler,
)

from unicon.bases.routers.connection import ENABLE_CRED_NAME

from unicon.plugins.utils import (get_current_credential,
    common_cred_password_handler, )

from unicon.core.errors import UniconAuthenticationError
from unicon.utils import to_plaintext



patterns = ASAPatterns()
settings = ASASettings()

def enable_password_handler(spawn, context, session):
    credentials = context.get('credentials')
    enable_credential = credentials[ENABLE_CRED_NAME] if credentials else None
    if enable_credential:
        try:
            spawn.sendline(to_plaintext(enable_credential['password']))
        except KeyError as exc:
            raise UniconAuthenticationError("No password has been defined "
                "for credential {}.".format(ENABLE_CRED_NAME))

    else:
        spawn.sendline(context['enable_password'])


def line_password_handler(spawn, context, session):
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(
            spawn=spawn, context=context, credential=credential,
            session=session)
    else:
        spawn.sendline(context['line_password'])

def escape_char_handler(spawn):
    """ handles telnet login messages
    """
    # Wait a small amount of time for any chatter to cease from the
    # device before attempting to call sendline.

    prev_buf_len = len(spawn.buffer)
    for retry_number in range(
            settings.ESCAPE_CHAR_CALLBACK_PAUSE_CHECK_RETRIES):
        time.sleep(settings.ESCAPE_CHAR_CALLBACK_PAUSE_SEC)
        spawn.read_update_buffer()
        cur_buf_len = len(spawn.buffer)
        if prev_buf_len == cur_buf_len:
            break
        else:
            prev_buf_len = cur_buf_len

    spawn.sendline()

login_password = Statement(pattern=patterns.line_password,
                           action=line_password_handler,
                           args=None,
                           loop_continue=True,
                           continue_timer=False)

enable_password = Statement(pattern=patterns.enable_password,
                            action=enable_password_handler,
                            args=None,
                            loop_continue=True,
                            continue_timer=False)

escape_char_stmt = Statement(pattern=patterns.escape_char,
                             action=escape_char_handler,
                             args=None,
                             loop_continue=True,
                             continue_timer=False)

press_return_stmt = Statement(pattern=patterns.press_return,
                              action=sendline, 
                              args=None,
                              loop_continue=True,
                              continue_timer=False)

connection_refused_stmt = Statement(pattern=patterns.connection_refused,
                                    action=connection_refused_handler,
                                    args=None,
                                    loop_continue=False,
                                    continue_timer=False)

bad_password_stmt = Statement(pattern=patterns.bad_passwords,
                              action=bad_password_handler,
                              args=None,
                              loop_continue=False,
                              continue_timer=False)

disconnect_error_stmt = Statement(pattern=patterns.disconnect_message,
                                  action=connection_failure_handler,
                                  args={
                                  'err': 'received disconnect from router'},
                                  loop_continue=False,
                                  continue_timer=False)
