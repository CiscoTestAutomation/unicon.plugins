"""
Statements for the Cisco Catalyst 9800-CL (vWLC) virtual controller.

The C9800-CL uses GRUB as its bootloader, identical to the CAT9KV platform.
Re-export the CAT9KV GRUB boot action so other c9800 modules have a stable
local import path.
"""

from unicon.plugins.iosxe.cat9kv.statements import (  # noqa: F401
    boot_from_rommon,
)
