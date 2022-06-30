"""
Module:
    unicon.plugins.junos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This module imports connection provider class which has
    exposes two methods named connect and disconnect. These
    methods are implemented in such a way so that they can
    handle majority of platforms and subclassing is seldom
    required.
"""
import time

from unicon.bases.routers.connection_provider import \
    BaseSingleRpConnectionProvider
from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog
from unicon.eal.expect import Spawn
from unicon.plugins.aos.statements import (aosConnection_statement_list,
                                           aosStatements)
from unicon.plugins.generic.statements import custom_auth_statements
import getpass

class aosSingleRpConnectionProvider(self):
    """ Implements Junos singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device.
            See statements.py for connnection statement lists  """  
        con = self.connection
        connection_dialogs = super().get_connection_dialog()
        connection_dialogs += Dialog(aosConnection_statement_list)

        return connection_dialogs