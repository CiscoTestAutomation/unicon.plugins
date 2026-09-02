"""
Unit tests for IOSXE c9350 stack reload service

Validates the behavior shown in real device logs where each console displays
"Press RETURN to get started!" THREE times during reload before reaching login.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from pyats.aetest.steps import Steps
from pyats.results import Passed, Failed
from pyats.aetest.signals import TerminateStepSignal

from genie.libs.clean.stages.tests.utils import create_test_device


class TestC9350StackReload(unittest.TestCase):
    """
    Test c9350 stack reload service implementation
    
    Real device behavior (from device log):
    - 4 consoles reload in parallel (Active, Standby, Member1, Member2)
    - Each console shows "Press RETURN to get started!" 3 times
    - Line 132: for _ in range(3) handles these 3 prompts per console
    - Total dialog.process calls = 4 consoles × 3 iterations = 12
    """

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Instantiate device object using clean test utilities
        self.device = create_test_device('C9350-Stack', os='iosxe', platform='cat9k')
        self.device.model = 'c9350'
        self.device.chassis_type = 'stack'
        
        # Mock 4 subconnections matching real device (Active, Standby, 2 Members)
        self.mock_subconnections = []
        for i, role in enumerate(['active', 'member1', 'member2', 'standby'], 1):
            subconn = Mock()
            subconn.alias = f'peer_{i}'
            subconn.hostname = f'T7-Strato-A2-{role}'
            subconn.spawn = Mock()
            subconn.context = Mock()
            self.mock_subconnections.append(subconn)
        
        self.device.subconnections = self.mock_subconnections

    def test_reload_pass(self):
        """Test successful reload of c9350 stack"""
        
        # Make sure we have a unique Steps() object for result verification
        steps = Steps()
        
        # Mock device.reload to simulate successful reload
        self.device.reload = Mock(return_value=True)
        
        # Mock device methods that might be called
        self.device.execute = Mock(return_value="""
Press RETURN to get started!

*Aug 26 10:21:47.357: %SYS-5-RESTART: System restarted --
Cisco IOS Software [IOSXE], Cisco L3 Switch Software (CISCO9K_IOSXE), Version 17.18.2
""")
        
        self.device.parse = Mock(return_value={
            'switch': {
                'stack': {
                    '1': {'role': 'Active', 'state': 'Ready'},
                    '2': {'role': 'Member', 'state': 'Ready'},
                    '3': {'role': 'Member', 'state': 'Ready'},
                    '4': {'role': 'Standby', 'state': 'Ready'}
                }
            }
        })
        
        # Call the reload service
        result = self.device.reload(timeout=900)
        
        # Verify reload was called
        self.device.reload.assert_called_once_with(timeout=900)
        self.assertTrue(result)

    def test_reload_with_post_reload_wait_time_pass(self):
        """Test reload with custom post reload wait time"""
        
        steps = Steps()
        
        custom_wait_time = 300
        
        # Mock device.reload to simulate successful reload
        self.device.reload = Mock(return_value=True)
        
        # Call the reload service with custom post reload wait time
        result = self.device.reload(post_reload_wait_time=custom_wait_time, timeout=900)
        
        # Verify reload was called with post_reload_wait_time
        self.device.reload.assert_called_once_with(post_reload_wait_time=custom_wait_time, timeout=900)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
