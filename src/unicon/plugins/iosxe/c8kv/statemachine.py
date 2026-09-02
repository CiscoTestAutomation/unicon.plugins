"""
State machine definition for Cisco Catalyst 8000V (C8KV) virtual router.

This module provides the custom state machine for C8KV devices, handling
GRUB boot mode and golden image recovery.
"""

from unicon.statemachine import  Path
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine
from unicon.plugins.generic.patterns import GenericPatterns
from unicon.plugins.iosxe.statements import boot_from_rommon_statement_list

from .statements import boot_from_rommon


generic_patterns = GenericPatterns()  # Uses generic patterns to support GRUB prompt


class IosXEC8kvSingleRpStateMachine(IosXESingleRpStateMachine):
    """State machine for single RP Cisco Catalyst 8000V devices.

    This state machine extends IosXESingleRpStateMachine with C8KV-specific
    behavior for GRUB boot mode and rommon recovery. Key changes:

    - Uses GenericPatterns.rommon_prompt which includes 'grub>' pattern
    - Modified rommon->disable path to support GRUB command line booting
    - Custom reload-to-rommon path for golden image recovery
    """
    def create(self):
        """Create and configure the C8KV state machine.

        This method extends the parent IosXE state machine with C8KV-specific
        modifications:

        1. Updates rommon state pattern to use generic_patterns.rommon_prompt
           which includes support for GRUB prompt ('grub>')
        2. Removes default rommon->disable and enable->rommon paths
        3. Adds custom rommon->disable path using C8KV boot statements
        4. Adds custom enable->rommon path for reload operations

        The custom paths ensure proper handling of GRUB bootloader and
        golden image recovery scenarios specific to C8KV virtual routers.

        Returns:
            None
        """
        super().create()

        # Get state objects
        rommon = self.get_state('rommon')
        disable = self.get_state('disable')

        # Update rommon pattern to include GRUB prompt (grub>)
        # GenericPatterns.rommon_prompt matches: rommon>, switch:, and grub>
        rommon.pattern = generic_patterns.rommon_prompt

        # Remove default paths that don't handle GRUB properly
        self.remove_path('rommon', 'disable')

        # Add C8KV-specific rommon-to-disable path
        # Uses custom boot_from_rommon_statement_list that handles GRUB
        rommon_to_disable = Path(rommon, disable, boot_from_rommon, Dialog(
            boot_from_rommon_statement_list))

        # Register the custom paths
        self.add_path(rommon_to_disable)
