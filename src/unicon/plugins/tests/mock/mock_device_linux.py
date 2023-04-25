import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)

class MockDeviceLinux(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='linux', **kwargs)


class MockDeviceTcpWrapperLinux(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'port' in kwargs:
            kwargs.pop('port')
        self.mockdevice = MockDeviceLinux(*args, **kwargs)


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--ha', action='store_true', help='HA mode')
        parser.add_argument('--hostname', help='Device hostname (default: Router')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    else:
        state = 'exec'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Linux'

    if args.ha:
        md = MockDeviceTcpWrapperLinux(hostname=hostname, state=state)
        md.run()
    else:
        md = MockDeviceLinux(hostname=hostname, state=state)
        md.run()


if __name__ == "__main__":
    main()
