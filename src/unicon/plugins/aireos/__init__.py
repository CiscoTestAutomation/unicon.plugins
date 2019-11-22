import time

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.bases.routers.connection_provider import BaseSingleRpConnectionProvider
from unicon.eal.dialogs import Dialog
from unicon.plugins.aireos.settings import AireosSettings
from unicon.plugins.aireos.statemachine import AireosStateMachine
from unicon.plugins.generic import ServiceList
from unicon.plugins.aireos import service_implementation as svc

from .patterns import AireosPatterns

from unicon.plugins.utils import (get_current_credential,
    common_cred_username_handler, common_cred_password_handler, )

p = AireosPatterns()


def wait_and_enter(spawn):
    time.sleep(0.5)  # otherwise newline is sometimes lost?
    spawn.sendline() # ctrl-d
    time.sleep(0.5)


def password_handler(spawn, context, session):
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(
            spawn=spawn, context=context, credential=credential,
            session=session)
    else:
        spawn.sendline(context['tacacs_password'])


def username_handler(spawn, context, session):
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_username_handler(
            spawn=spawn, context=context, credential=credential)
    else:
        spawn.sendline(context['username'])


class AireosConnectionProvider(BaseSingleRpConnectionProvider):
    def get_connection_dialog(self):
        return Dialog([
            [self.connection.settings.PASSWORD_PROMPT \
                if self.connection.settings.PASSWORD_PROMPT else p.password,
                password_handler,
                None, True, False],
            [self.connection.settings.LOGIN_PROMPT \
                if self.connection.settings.LOGIN_PROMPT else p.user,
                username_handler,
                None, True, False],
            [p.bare,
                None, None, False, False],
            [p.shell,
                lambda spawn: spawn.sendline('exit'),
                None, False, False],
            [p.mode,
                lambda spawn: spawn.sendline('exit'),
                None, False, False],
            [p.escape_char,
                wait_and_enter,
                None, True, False]])


class AireosServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.AireosReload
        self.ping = svc.AireosPing
        self.copy = svc.AireosCopy


class AireosConnection(BaseSingleRpConnection):
    os = 'aireos'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = AireosStateMachine
    connection_provider_class = AireosConnectionProvider
    subcommand_list = AireosServiceList
    settings = AireosSettings()
