""" Generic IOS-XE Service Statements """

__author__ = "Myles Dear <pyats-support@cisco.com>"

import re

from unicon.eal.dialogs import Statement
from .patterns import IosXEPatterns

patterns = IosXEPatterns()


def boot_image(spawn, context, session):
    if not context.get('boot_prompt_count'):
        context['boot_prompt_count'] = 1
    if context.get('boot_prompt_count') < \
            spawn.settings.MAX_BOOT_ATTEMPTS:
        if "image_to_boot" in context:
            cmd = "boot {}".format(context['image_to_boot']).strip()
        elif spawn.settings.FIND_BOOT_IMAGE:
            spawn.sendline('dir flash:')
            dir_listing = spawn.expect('.* bytes used').match_output
            m = re.search(r'(\S+\.bin)[\r\n]', dir_listing)
            if m:
                boot_image = m.group(1)
                cmd = "boot flash:{}".format(boot_image)
            else:
                cmd = "boot"
        else:
            cmd = "boot"
        spawn.sendline(cmd)
        context['boot_prompt_count'] += 1
    else:
        raise Exception("Too many failed boot attempts have been detected.")



overwrite_previous = Statement(pattern=patterns.overwrite_previous,
                               action='sendline()',
                               loop_continue=True,
                               continue_timer=False)

delete_filename = Statement(pattern=patterns.delete_filename,
                            action='sendline()',
                            loop_continue=True,
                            continue_timer=False)

confirm = Statement(pattern=patterns.confirm,
                    action='sendline()',
                    loop_continue=True,
                    continue_timer=False)

are_you_sure = Statement(pattern=patterns.are_you_sure,
                         action='sendline(y)',
                         loop_continue=True,
                         continue_timer=False)

are_you_sure_ywtdt = Statement(pattern=patterns.are_you_sure_ywtdt,
                               action='sendline(yes)',
                               loop_continue=True,
                               continue_timer=False)

wish_continue = Statement(pattern=patterns.wish_continue,
                          action='sendline(yes)',
                          loop_continue=True,
                          continue_timer=False)

want_continue = Statement(pattern=patterns.want_continue,
                          action='sendline(yes)',
                          loop_continue=True,
                          continue_timer=False)

press_enter = Statement(pattern=patterns.press_enter,
                        action='sendline()',
                        loop_continue=True,
                        continue_timer=False)


configure_statement_list = [
    are_you_sure,
    wish_continue,
    confirm,
    want_continue,
    are_you_sure_ywtdt
]

execute_statement_list = [
    overwrite_previous,
    delete_filename,
    confirm,
    want_continue
]
