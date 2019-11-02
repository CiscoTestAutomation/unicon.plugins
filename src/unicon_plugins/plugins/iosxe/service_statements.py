""" Generic IOS-XE Service Statements """

__author__ = "Myles Dear <pyats-support@cisco.com>"


from unicon.eal.dialogs import Statement
from .patterns import IosXEPatterns

patterns = IosXEPatterns()

# loop_continue is set to `True` to ensure the dialog does not end up
# prematurely terminating, which can mess up things like executing the
# "write memory" command.
overwrite_previous = Statement(pattern=patterns.overwrite_previous,
                               action='sendline()',
                               loop_continue=True,
                               continue_timer=False)


delete_filename = Statement(pattern=patterns.delete_filename,
                            action='sendline()',
                            loop_continue=True,
                            continue_timer=False)

# loop_continue is set to `True` to ensure the dialog does not end up
# prematurely terminating, which can mess up things like uniclean
# successive file deletion.
confirm = Statement(pattern=patterns.confirm,
                    action='sendline()',
                    loop_continue=True,
                    continue_timer=False)

are_you_sure = Statement(pattern=patterns.are_you_sure,
                         action='sendline(y)',
                         loop_continue=False,
                         continue_timer=False)

wish_continue = Statement(pattern=patterns.wish_continue,
                          action='sendline(yes)',
                          loop_continue=False,
                          continue_timer=False)

want_continue = Statement(pattern=patterns.want_continue,
                          action='sendline(yes)',
                          loop_continue=False,
                          continue_timer=False)

press_enter = Statement(pattern=patterns.press_enter,
                        action='sendline()',
                        loop_continue=True,
                        continue_timer=False)

