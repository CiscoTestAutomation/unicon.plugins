__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"

import re

from unicon.eal.dialogs import Statement
from .patterns import IosXECat3kPatterns
from .setting import IosXECat3kSettings

patterns = IosXECat3kPatterns()
settings = IosXECat3kSettings()


def boot_image(spawn, context, session):
    if not context.get('boot_prompt_count'):
        context['boot_prompt_count'] = 1
    if context.get('boot_prompt_count') < \
            settings.MAX_ALLOWABLE_CONSECUTIVE_BOOT_ATTEMPTS:
        if "image_to_boot" in context:
            cmd = "boot {}".format(context['image_to_boot'])
        else:
            spawn.sendline('dir flash:')
            dir_listing = spawn.expect('.* bytes used').match_output
            m = re.search(r'(\S+\.bin)[\r\n]', dir_listing)
            if m:
                boot_image = m.group(1)
                cmd = "boot flash:{}".format(boot_image)
            else:
                cmd = "boot"
        spawn.sendline(cmd)
        context['boot_prompt_count'] += 1
    else:
        raise Exception("Too many failed boot attempts have been detected.")

boot_reached = Statement(pattern=patterns.rommon_prompt,
                         action=boot_image,
                         loop_continue=True,
                         continue_timer=False)

access_shell = Statement(pattern=patterns.access_shell,
                         action=lambda spawn: spawn.sendline("y"),
                         loop_continue=True,
                         continue_timer=False)

tcpdump_continue = Statement(pattern=patterns.tcpdump,
                             action=lambda spawn: spawn.sendline(""),
                             loop_continue=False,
                             continue_timer=False)
