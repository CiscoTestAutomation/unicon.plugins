"""
Module:
    unicon.plugins.tests.test_plugin_ironware

Author:
    James Di Trapani <james@ditrapani.com.au> - https://github.com/jamesditrapani

Description:
    Perform Unit Testing on Ironware Services
"""

__author__ = "James Di Trapani <james@ditrapani.com.au>"

import os
import yaml
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path
from unicon.core.errors import SubCommandFailure

with open(os.path.join(mockdata_path, 'ironware/ironware_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestIronWarePluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='mlx8',
                        start=['mock_device_cli --os ironware --state exec'],
                        os='ironware',
                        credentials={
                            'default': {
                                'username': 'ironware1',
                                'password': 'pyatsRocks!'
                            },
                            'enable': {
                                'password': 'pyatsRocks!'
                            }
                        })
        c.connect()
        self.assertIn('mlx8#', c.spawn.match.match_output)

    def test_login_connect_ssh(self):
        c = Connection(hostname='mlx8',
                        start=['mock_device_cli --os ironware --state connect_ssh'],
                        os='ironware',
                        credentials={
                            'default': {
                                'username': 'ironware1',
                                'password': 'pyatsRocks!'
                            },
                            'enable': {
                                'password': 'pyatsRocks!'
                            }
                        })
        c.connect()
        self.assertIn('mlx8#', c.spawn.match.match_output)

    def test_login_connect_connectReply(self):
        c = Connection(hostname='mlx8',
                        start=['mock_device_cli --os ironware --state exec'],
                        os='ironware',
                        credentials={
                            'default': {
                                'username': 'ironware1',
                                'password': 'pyatsRocks!'
                            },
                            'enable': {
                                'password': 'pyatsRocks!'
                            }
                        },
                        connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

class TestIronWarePluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        c = Connection(hostname='mlx8',
                        start=['mock_device_cli --os ironware --state exec'],
                        os='ironware',
                        credentials={
                            'default': {
                                'username': 'ironware1',
                                'password': 'pyatsRocks!'
                            },
                            'enable': {
                                'password': 'pyatsRocks!'
                            }
                        },
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        cmd = 'show ip route'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)

class TestIronWarePluginMPLSPing(unittest.TestCase):

    def test_mpls_ping_success(self):
        c = Connection(hostname='mlx8',
                            start=['mock_device_cli --os ironware --state exec'],
                            os='ironware',
                            credentials={
                                'default': {
                                    'username': 'ironware1',
                                    'password': 'pyatsRocks!'
                                },
                                'enable': {
                                    'password': 'pyatsRocks!'
                                }
                            })
        c.mpls_ping(lsp='mlx8.1_to_ces.2')
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()),"""ping mpls rsvp lsp mlx8.1_to_ces.2
Send 5 96-byte MPLS Echo Requests over RSVP LSP mlx8.1_to_ces.2, timeout 5000 msec
Type Control-c to abort
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max=0/1/3 ms
mlx8#""")

    def test_mpls_ping_failure(self):
        c = Connection(hostname='mlx8',
                            start=['mock_device_cli --os ironware --state exec'],
                            os='ironware',
                            credentials={
                                'default': {
                                    'username': 'ironware1',
                                    'password': 'pyatsRocks!'
                                },
                                'enable': {
                                    'password': 'pyatsRocks!'
                                }
                            })
        try:
            c.mpls_ping(lsp='mlx8.1_to_mlx8.4')
        except SubCommandFailure:
            pass
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()),"""ping mpls rsvp lsp mlx8.1_to_mlx8.4
Ping fails: LSP is down
mlx8#""")

if __name__ == "__main__":
    unittest.main()
