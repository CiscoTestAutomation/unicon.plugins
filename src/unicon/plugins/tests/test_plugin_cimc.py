"""
Unittests for cimc plugin

Uses the mock_device.py script to test the plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import unittest

from unicon import Connection
from unicon.core.errors import SubCommandFailure


class TestCimcPlugin(unittest.TestCase):

    def test_connect(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os cimc --state cimc_connect'],
                            os='cimc')
        c.connect()
        self.assertEqual(c.spawn.match.match_output.splitlines()[-1], 'Compute-Node-1#')
        return c

    def test_execute(self):
        c = self.test_connect()
        c.execute('scope chassis')
        self.assertEqual(c.spawn.match.match_output.splitlines()[-1], 'Compute-Node-1 /chassis # ')

    def test_execute_with_yes_no(self):
        c = self.test_connect()
        c.execute('scope vmedia')
        c.execute('unmap testmap')
        self.assertEqual(c.spawn.match.match_output.splitlines()[-1], 'Compute-Node-1 /vmedia # ')

    # Verify that device prompt/hostname isn't returned by execute
    def test_prompt_stripping(self):
        c = self.test_connect()
        output = c.execute('show foo')
        self.assertEqual(output, 'This is some output')

if __name__ == "__main__":
    unittest.main()
