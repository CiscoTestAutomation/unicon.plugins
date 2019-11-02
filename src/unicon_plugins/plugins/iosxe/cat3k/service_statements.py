__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"


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
        cmd = "boot {}".format(context['image_to_boot']) \
            if "image_to_boot" in context else "boot"
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
