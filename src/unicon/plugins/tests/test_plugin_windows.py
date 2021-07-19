"""
Unittests for windows plugin

Uses the mock_device.py script to test the plugin.

"""

__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "dwapstra"


import unittest

from unicon import Connection
from unicon.core.errors import SubCommandFailure


class TestWindowsPluginConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='WIN7',
                           start=['mock_device_cli --os windows --state windows_connect'],
                           os='windows',
                           credentials={'default': {'usernane': 'cisco', 'password': 'cisco'}}
                           )

        cls.c.connect()

    def test_execute(self):
        r = self.c.execute('dir')
        self.assertEqual(len(r), 1202)


if __name__ == "__main__":
    unittest.main()

