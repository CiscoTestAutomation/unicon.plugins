"""
State machine definition for Cisco Catalyst 9000V (CAT9KV) virtual switch.

This module provides the custom state machine for CAT9KV devices, handling
GRUB boot mode and golden image recovery.
"""

from unicon.statemachine import Path
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine
from unicon.plugins.generic.patterns import GenericPatterns
from unicon.plugins.iosxe.statements import boot_from_rommon_statement_list

from .statements import boot_from_rommon


generic_patterns = GenericPatterns()  # Uses generic patterns to support GRUB prompt


class IosXECat9kvSingleRpStateMachine(IosXESingleRpStateMachine):
    """State machine for single RP Cisco Catalyst 9000V devices.

    This state machine extends IosXESingleRpStateMachine with CAT9KV-specific
    behavior for GRUB boot mode and rommon recovery. Key changes:

    - Uses GenericPatterns.rommon_prompt which includes 'grub>' pattern
    - Modified rommon->disable path to support GRUB menu booting
    """
    def create(self):
        """Create and configure the CAT9KV state machine."""
        super().create()

        # Get state objects
        rommon = self.get_state('rommon')
        disable = self.get_state('disable')

        # Update rommon pattern to include GRUB prompt (grub>)
        # GenericPatterns.rommon_prompt matches: rommon>, switch:, and grub>
        rommon.pattern = generic_patterns.rommon_prompt

        # Remove default path that does not handle GRUB properly
        self.remove_path('rommon', 'disable')

        # Add CAT9KV-specific rommon-to-disable path
        # Uses custom boot_from_rommon action that sends ESC for GRUB
        rommon_to_disable = Path(rommon, disable, boot_from_rommon, Dialog(
            boot_from_rommon_statement_list))

        # Register the custom path
        self.add_path(rommon_to_disable)
