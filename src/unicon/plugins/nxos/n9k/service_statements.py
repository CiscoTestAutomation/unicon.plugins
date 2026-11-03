__author__ = 'Difu Hu <difhu@cisco.com>'

from copy import copy

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import generic_statements
from unicon.plugins.nxos.patterns import NxosPatterns
from unicon.plugins.nxos.service_statements import (
    admin_password, secure_password)

from .setting import Nxos9kSettings

patterns = NxosPatterns()
settings = Nxos9kSettings()


def secure_password_setup(spawn, session, response):
    session['n9k_password_setup_pending'] = True
    secure_password.action(spawn, response=response)


def admin_password_setup(spawn, context, session):
    session['n9k_password_setup_pending'] = True
    admin_password.action(spawn, context, session)
    if spawn.match.last_match.group(2) == 'Confirm':
        session.pop('n9k_password_setup_pending', None)


def setup_syslog(spawn, session):
    if session.get('n9k_password_setup_pending'):
        generic_statements.syslog_stripper_stmt.action(spawn)
        session['syslog_sent_cr'] = False
    else:
        # Boot syslogs can precede the setup question by a few seconds.
        # Allow that question to arrive before the generic handler sends a
        # Return, which would accept its default 'yes'. A standalone syslog
        # still gets prompt recovery after the boot setup quiet period.
        generic_statements.syslog_msg_stmt.action(
            spawn, session, wait_time=spawn.settings.BOOT_SETUP_SYSLOG_WAIT)


secure_password_setup_stmt = copy(secure_password)
secure_password_setup_stmt.action = secure_password_setup

admin_password_setup_stmt = copy(admin_password)
admin_password_setup_stmt.action = admin_password_setup

setup_syslog_stmt = copy(generic_statements.syslog_msg_stmt)
setup_syslog_stmt.action = setup_syslog


def boot_image(spawn, context, session):
    session.setdefault('boot_attempt_count', 0)
    if session.get('boot_attempt_count') < settings.MAX_BOOT_ATTEMPTS:
        cmd = 'boot {}'.format(context['image_to_boot']) \
            if 'image_to_boot' in context else ''
        spawn.sendline(cmd)
        session['boot_attempt_count'] += 1
    else:
        err_info = 'Too many failed boot attempts have been detected.' \
            if 'image_to_boot' in context \
            else 'Got loader prompt but image_to_boot parameter was not provided.'
        raise Exception(err_info)


loader = Statement(pattern=patterns.loader_prompt,
                   action=boot_image,
                   args=None,
                   loop_continue=True,
                   continue_timer=False)
