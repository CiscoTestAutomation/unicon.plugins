
from unicon.statemachine import Path, State
from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.patterns import GenericPatterns
from unicon.plugins.iosxe.statements import boot_from_rommon_statement_list
from unicon.plugins.iosxe.cat9k.statemachine import IosXECat9kSingleRpStateMachine
from unicon.plugins.iosxe.cat9k.statements import reload_to_rommon_statement_list
from .statements import boot_from_rommon


generic_patterns = GenericPatterns()


class IosXEc9800SingleRpStateMachine(IosXECat9kSingleRpStateMachine):
    """State machine for single RP Cisco Catalyst 9800-CL (vWLC) controllers.

    The C9800-CL is a virtual platform that boots via the GRUB bootloader
    rather than the traditional ROMMON used on physical Catalyst 9000 switches.
    The inherited cat9k rommon->disable path sends a ``boot`` command which has
    no effect at the ``grub>`` prompt, so it is replaced with a GRUB-aware path
    that sends ESC to bring up the boot menu and selects the boot entry.
    """

    def create(self):
        super().create()

        enable = self.get_state('enable')
        disable = self.get_state('disable')

        # Remove inherited rommon state and its paths (cat9k rommon uses
        # a pattern without grub> and a boot command invalid at GRUB)
        self.remove_path('rommon', 'disable')
        self.remove_path('enable', 'rommon')
        self.remove_state('rommon')

        # Create new rommon state with GRUB prompt support
        # GenericPatterns.rommon_prompt matches: rommon>, switch:, and grub>
        rommon = State('rommon', generic_patterns.rommon_prompt)
        self.add_state(rommon)

        # Add C9800-CL-specific rommon-to-disable path
        # Uses GRUB-aware boot_from_rommon action that sends ESC for GRUB
        rommon_to_disable = Path(rommon, disable, boot_from_rommon, Dialog(
            boot_from_rommon_statement_list))
        self.add_path(rommon_to_disable)

        # Re-add enable-to-rommon path (removed with old rommon state)
        enable_to_rommon = Path(enable, rommon, 'reload', Dialog(
            reload_to_rommon_statement_list))
        self.add_path(enable_to_rommon)
