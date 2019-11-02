
class NxosvReloadPatterns:
    """ NXOSv related patterns. """

    def __init__ (self):
        # Relaxed patterns, for example the following line was
        # seen on a NXOSv console during startup:
        # login: 2016 Sep 27 14:07:35 switch %PLATFORM-2-MOD_DETECT: Module 2 detected (Serial number TM00C39B67C) Module-Type NX-OSv Ethernet Module Model N7K-F248XP-25
        self.username = r'^.*([Uu]sername|[Ll]ogin): ?'
        self.password = r'^.*[Pp]assword: ?'
