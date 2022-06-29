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


class aosSingleRpConnectionProvider(BaseSingleRpConnectionProvider):
    """ Implements Junos singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, connection,
                     dialog=Dialog([]),
                     timeout=20,
                     *args, **kwargs):
        con = self.connection
        password="assword:"
        response="yes"
        fingerprint="(yes/no/[fingerprint])?"
        continues="Press any key to continue"
        prompt="#"
        #s = Spawn(spawn_command="ssh alp041@10.119.95.7")
        d = str(dialog)
        e =  str(con)
        print(d)
        print(e)
        if dialog is None:
            con.spawn.sendline(command)
            time.sleep(2)
            self.result = con.spawn.expect(".*$")
            time.sleep(2)
            t = str(self.result)
            print(t)
            try:
                if fingerprint in t:
                    print(t)
                    con.send(response + "\r")
                    time.sleep(1)
                    t = str(con.expect([r".*$"]))
                if password in t:
                    print(t)
                    con.send(secret + "\r")
                    time.sleep(1)
                    t = str(con.expect([r".*$"]))
                if continues in t:
                    print(t)
                    con.sendline()
                    con.sendline()
                    time.sleep(1)
                    t = str(con.expect([r".*$"]))
                if prompt in t:
                    con.sendline("show vlan")
                    t = str(con.expect([r".*$"]))
                    print(t)
                    s.close()
            except TimeoutError as err:
                print('errored becuase of timeout')
        else:
            self.result = dialog.proces(con.spawn, timeout=timeout)

