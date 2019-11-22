__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.iosxr.connection_provider \
    import IOSXRSingleRpConnectionProvider, IOSXRDualRpConnectionProvider
from unicon.plugins.iosxr.connection_provider \
    import IOSXRVirtualConnectionProviderLaunchWaiter
from unicon.plugins.iosxr.statements import IOSXRStatements
from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.plugins.iosxr.errors import RpNotRunningError
from unicon.eal.dialogs import Dialog
from random import randint
import time, re

patterns = IOSXRPatterns()
ACTIVE_RP_STATE = 'RUNNING'


class IOSXRVSingleRpConnectionProvider(
        IOSXRSingleRpConnectionProvider,
        IOSXRVirtualConnectionProviderLaunchWaiter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def establish_connection(self):
        """ Wait for virtual platform to come online before connecting. """
        con = self.connection
        settings = con.settings
        learn_hostname = con.learn_hostname
        con.log.info('Waiting for %s seconds before attempting to connect..' % settings.SLEEP_PRE_LAUNCH)
        time.sleep(settings.SLEEP_PRE_LAUNCH)
        self.wait_for_launch_complete(
            initial_discovery_wait_sec = \
                settings.INITIAL_LAUNCH_DISCOVERY_WAIT_SEC,
            initial_wait_sec = settings.INITIAL_LAUNCH_WAIT_SEC,
            post_prompt_wait_sec = settings.POST_PROMPT_WAIT_SEC,
            connection = con, log=con.log, hostname=con.hostname,
            checkpoint_pattern=patterns.logout_prompt,
            learn_hostname=learn_hostname)
        super().establish_connection()


class IOSXRVDualRpConnectionProvider(
        IOSXRDualRpConnectionProvider,
        IOSXRVirtualConnectionProviderLaunchWaiter):

    def establish_connection(self):
        """ Wait for virtual platform to come online before connecting. """
        connection = self.connection
        settings = connection.settings
        log = connection.log
        hostname = connection.hostname
        learn_hostname = connection.learn_hostname

        for con in [self.connection.a, self.connection.b]:
            self.wait_for_launch_complete(
                initial_discovery_wait_sec = \
                    settings.INITIAL_LAUNCH_DISCOVERY_WAIT_SEC,
                initial_wait_sec = settings.INITIAL_LAUNCH_WAIT_SEC,
                post_prompt_wait_sec = settings.POST_PROMPT_WAIT_SEC,
                connection = con, log=log, hostname=hostname,
                checkpoint_pattern=patterns.logout_prompt,
                learn_hostname=learn_hostname)
        super().establish_connection()
