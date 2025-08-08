"""
Unittests for Generic/IOSXE plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test IOSXE plugin.

"""

import unittest

from pyats.topology import loader
import unicon
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXESVLSwitchover(unittest.TestCase):

    def test_svl_stack_switchover(self):

        md = MockDeviceTcpWrapperIOSXE(port=0, state='svl_stack_enable' + ',svl_stby_enable', stackwise_virtual=True)
        md.start()
        testbed = '''
            devices:
              Router:
                type: router
                os: iosxe
                platform: cat9k
                model: c9500
                submodel: c9500x
                chassis_type: stackwise_virtual
                connections:
                  defaults:
                    class: 'unicon.Unicon'
                    connections: [p1, p2, p3]
                  p1:
                    protocol: telnet
                    ip: 127.0.0.1
                    port: {}
                    member: 1
                  p2:
                    protocol: telnet
                    ip: 127.0.0.1
                    port: {}
                    member: 2
                credentials:
                  default:
                    username: cisco
                    password: cisco
            '''.format(md.ports[0], md.ports[1])
        t = loader.load(testbed)
        d = t.devices.Router

        d.connect()
        self.assertTrue(d.active.alias == 'p2')

        d.settings.POST_SWITCHOVER_SLEEP = 1
        d.execute('term width 0')
        d.configure('no logging console')
        d.switchover(timeout=10)
        d.disconnect()
        md.stop()


if __name__ == "__main__":
    unittest.main()
