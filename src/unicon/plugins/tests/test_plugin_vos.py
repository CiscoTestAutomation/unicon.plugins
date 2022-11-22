"""
Unittests for VOS plugin

Uses the unicon.plugins.tests.mock.mock_device_vos script to test the plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import os
import yaml
import unicon
import unittest
from textwrap import dedent

from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'vos/vos_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestVosPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='ucm',
                        start=['mock_device_cli --os vos --state vos_connect'],
                        os='vos',
                        username='admin',
                        tacacs_password='lab')
        cls.c.connect()

    def test_execute_with_paging(self):
        self.maxDiff = None
        output = self.c.execute('show tech dbstateinfo')
        self.assertEqual(output.splitlines(), """\
------------------------ Show tech dbstateinfo -------------------


Database State Info

Output is in /cm/trace/dbl/showtechdbstateinfo211506.txt
 
 Please use "file view activelog /cm/trace/dbl/showtechdbstateinfo211506.txt" to see the 
    contents of File
 
 Error Output is in /cm/trace/dbl/showtechdbstateinfo_cdr_err211506.out

Please use "file view activelog /cm/trace/dbl/showtechdbstateinfo_cdr_err211506.out" command to see the contents of File
""".splitlines())

    def test_execute_with_continue(self):
        r = self.c.execute('utils core active analyze')
        self.assertEqual(r.rstrip().replace('\r', ''),
            mock_data['vos_exec']['commands']['utils core active analyze']['response']+
            mock_data['continue_prompt']['prompt'] + 'y')

    def test_command_post_processing(self):
        r = self.c.execute('some command')
        self.assertEqual(type(r), str)
        r = self.c.execute(['some command', 'some command'])
        self.assertEqual(type(r), list)
        r = self.c.execute(['some command', 'some other command'])
        self.assertEqual(type(r), dict)
        r = self.c.execute(['some command', 'some other command', 'some other command'])
        self.assertEqual(type(r), dict)
        self.assertEqual(type(r['some other command']), list)


if __name__ == "__main__":
    unittest.main()

