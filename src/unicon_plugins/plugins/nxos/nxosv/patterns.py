from ..patterns import NxosPatterns

class NxosvPatterns(NxosPatterns):
    def __init__(self):
        super().__init__()

        # Relaxing this prompt, saw the following line in the nxosv log:
        # switch# 2016 Sep 28 18:37:47 switch %PLATFORM-2-MOD_DETECT: Module 3 detected (Serial number TM0024CC3FD) Module-Type NX-OSv Ethernet Module Model N7K-F248XP-25
        self.enable_prompt = r'^(.*?)(Router|Router-stby|Router-sdby|RouterRP|RouterRP-standby|%N-standby|%N\(standby\)|%N-sdby|(S|s)witch|(S|s)witch\(standby\)|Controller|ios|-Slot[0-9]+|%N)(\(boot\))*#.*$'

