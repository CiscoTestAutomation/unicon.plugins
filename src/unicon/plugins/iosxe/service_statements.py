""" Generic IOS-XE Service Statements """

__author__ = "Myles Dear <pyats-support@cisco.com>"

from unicon.eal.dialogs import Statement
from .patterns import IosXEPatterns

patterns = IosXEPatterns()


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

do_you_want_to = Statement(pattern=patterns.do_you_want_to,
                           action='sendline(y)',
                           loop_continue=True,
                           continue_timer=False)

proceed_confirm_stmt = Statement(pattern=patterns.proceed_confirm,
                                 action='sendline(yes)',
                                 loop_continue=True,
                                 continue_timer=False)

configure_statement_list = [
    are_you_sure,
    wish_continue,
    confirm,
    want_continue,
    are_you_sure_ywtdt,
    proceed_confirm_stmt
]

execute_statement_list = [
    overwrite_previous,
    delete_filename,
    confirm,
    want_continue,
    do_you_want_to
]
