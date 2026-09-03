
import unittest

import unicon
from unicon import Connection

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestPluginIosXeCat9kC9100AP(unittest.TestCase):

    def test_connect(self):
        conn = Connection(
            hostname='EWC',
            os='iosxe',
            platform='cat9k',
            model='c9100ap',
            start=['mock_device_cli --os iosxe --state ewc_enable'],
            learn_hostname=True)
        conn.connect()
        conn.disconnect()

    def test_ap_shell(self):
        conn = Connection(
            hostname='EWC',
            os='iosxe',
            platform='cat9k',
            model='c9100ap',
            start=['mock_device_cli --os iosxe --state ewc_enable'],
            credentials=dict(ap=dict(username='lab', password='lab', enable_password='lab')),
            learn_hostname=True)
        conn.connect()

        with conn.ap_shell() as ap:
            ap.execute('show interfaces wired 0')

        conn.disconnect()

    def test_bash_console(self):
        conn = Connection(
            hostname='EWC',
            os='iosxe',
            platform='cat9k',
            model='c9100ap',
            start=['mock_device_cli --os iosxe --state ewc_enable'],
            credentials=dict(ap=dict(username='lab', password='lab', enable_password='lab')),
            learn_hostname=True)
        conn.connect()

        with conn.bash_console() as bash:
            bash.execute('help')

        conn.disconnect()
