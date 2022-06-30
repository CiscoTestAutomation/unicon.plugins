"""
Module:
    unicon.plugins.generic

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This subpackage implements services specific to NXOS

"""

import io
import re
import collections
import warnings
import logging

from time import sleep
from datetime import datetime, timedelta

from unicon.bases.routers.services import BaseService
from unicon.plugins.generic.service_implementation import (
    BashService as GenericBashService)
from unicon.core.errors import (SubCommandFailure, TimeoutError,
    UniconAuthenticationError)

from unicon.logs import UniconStreamHandler, UNICON_LOG_FORMAT

from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.service_implementation import \
    Execute as GenericExecute
from unicon.plugins.generic.service_implementation import \
    GetMode as GenericGetMode
from unicon.plugins.generic.service_implementation import \
    GetRPState as GenericGetRPState
from unicon.plugins.generic.service_implementation import \
    Configure as GenericConfigure
from unicon.plugins.generic.service_statements import ping6_statement_list, \
    switchover_statement_list, standby_reset_rp_statement_list
from unicon.plugins.generic.statements import buffer_settled
from unicon.plugins.generic.service_statements import send_response
from unicon.plugins.nxos.service_statements import nxos_reload_statement_list, \
    ha_nxos_reload_statement_list, execute_stmt_list
from unicon.settings import Settings
from unicon.utils import (AttributeDict, pyats_credentials_available,
    to_plaintext)
from .patterns import aosPatterns

import unicon.plugins.nxos

patterns = aosPatterns()
settings = Settings()
    
    
def __init__(self, connection, context, **kwargs):
    super().__init__(connection, context, **kwargs)
    self.start_state = 'enable'
    self.end_state = 'enable'