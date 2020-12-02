import argparse

from unicon.mock.mock_device import MockDevice

class MockDeviceIOSXREnxr(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def main(args=None):
        if not args:
            parser = argparse.ArgumentParser()
            parser.add_argument('--state', help='initial state')
            parser.add_argument('--ha', action='store_true', help='HA mode')
            parser.add_argument('--hostname', help='Device hostname (default: Router')
            args = parser.parse_args()

        if args.state:
            state = args.state
        else:
            state = 'exec,exec_standby'

        if args.hostname:
            hostname = args.hostname
        else:
            hostname = 'Router'

        if args.ha:
            md = MockDeviceTcpWrapperIOSXREnxr(hostname=hostname, state=state)
            md.run()
        else:
            md = MockDeviceIOSXREnxr(hostname=hostname, state=state)
            md.run()


    if __name__ == "__main__":
        main()
