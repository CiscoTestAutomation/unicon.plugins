"""
Unittests for aireos plugin

"""

import os
import re
import unittest

from unicon import log, Connection
from unicon.core.errors import SubCommandFailure


class TestAireOsPlugin(unittest.TestCase):

    def test_connect(self):
        c = Connection(hostname='Controller',
                       start=['mock_device_cli --os aireos --state aireos_exec'],
                       os='aireos',
                       username='lab')
        c.connect()

    def test_reload(self):
        c = Connection(hostname='Controller',
                       start=['mock_device_cli --os aireos --state aireos_exec'],
                       os='aireos',
                       username='lab')
        c.connect()

    def test_reload_credentials(self):
        c = Connection(hostname='Controller',
                       start=['mock_device_cli --os aireos --state aireos_exec'],
                       os='aireos',
                       credentials=dict(default=dict(
                           username='lab', password='lab')))
        c.connect()
        c.reload()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
