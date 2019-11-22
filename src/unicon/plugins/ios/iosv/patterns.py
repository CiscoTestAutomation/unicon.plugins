__author__ = "Myles Dear <mdear@cisco.com>"

import re

from unicon.plugins.generic.patterns import GenericPatterns
from unicon.plugins.generic.service_patterns import ReloadPatterns


class IosvPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.rommon_prompt = r'(.*)switch:\s?$'
        self.shell_prompt = r'(.*?)\[%N.*\]\$\s?$'
        self.access_shell = r'.*Are you sure you want to continue\? \[y/n\]\s?'
        self.overwrite_previous = r'.*Overwrite the previous NVRAM configuration\?\[confirm\]'
        self.are_you_sure = r'Are you sure you want to continue\? \(y\/n\)\[y\]:\s?$'
        self.delete_filename = r'.*Delete filename \[.*\]\?\s*$'
        self.confirm = r'.*\[confirm\]\s*$'
        self.wish_continue = r'.*Do you wish to continue\? \[yes\]:\s*$'
        self.want_continue = r'.*Do you want to continue\? \[no\]:\s*$'
        self.press_enter = ReloadPatterns().press_enter
        self.dest_file_startup = \
            r'.*Destination filename \[startup-config\]\?\s*$'
        self.machine_id = r"Machine ID: (\d+)"

        # Relaxing these prompts, saw the following line in the iosv logs:
        # Router> state to administratively down
        self.enable_prompt = r'^(.*?)(Router|Router-stby|Router-sdby|RouterRP|RouterRP-standby|%N-standby|%N\(standby\)|%N-sdby|(S|s)witch|(S|s)witch\(standby\)|Controller|ios|-Slot[0-9]+|%N)(\(boot\))*#.*$'
        self.disable_prompt = r'^(.*?)(Router|Router-stby|Router-sdby|RouterRP|RouterRP-standby|%N-standby|%N-sdby|(S|s)witch|s(S|s)witch\(standby\)|Controller|ios|-Slot[0-9]+|%N)(\(boot\))*>.*$'
