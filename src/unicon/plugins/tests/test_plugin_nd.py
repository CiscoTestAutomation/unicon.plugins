"""
Unittests for ND plugin

Uses the mock_device.py script to test the execute service.

"""

__author__ = "Romel Tolos <rtolos@cisco.com>"

import os
import re
import yaml
import datetime
import unittest
import importlib
from pprint import pformat

from concurrent.futures import ThreadPoolExecutor
multiprocessing = __import__('multiprocessing').get_context('fork')

from unittest.mock import Mock, call, patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure, ConnectionError as UniconConnectionError
from unicon.plugins.linux.patterns import LinuxPatterns
from unicon.plugins.linux.settings import LinuxSettings
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'nd/nd_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestNDPluginConnect(unittest.TestCase):

    def test_connect_ssh(self):
        c = Connection(hostname='nd',
                       start=['mock_device_cli --os nd --state connect_ssh'],
                       os='nd',
                       username='admin',
                       password='cisco')
        c.connect()
        c.disconnect()

    def test_connect_sma(self):
        c = Connection(hostname='sma03',
                       start=['mock_device_cli --os nd --state connect_sma'],
                       os='nd',
                       username='admin',
                       password='cisco')
        c1 = Connection(hostname='pod-esa01',
                        start=['mock_device_cli --os nd --state connect_sma'],
                        os='nd',
                        username='admin',
                        password='cisco1')
        c.connect()
        c1.connect()
        c.disconnect()
        c1.disconnect()

    def test_connect_for_password(self):
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os nd --state connect_for_password'],
                       os='nd',
                       username='admin',
                       password='cisco')
        c.connect()
        c.disconnect()

    def test_bad_connect_for_password(self):
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os nd --state connect_for_password'],
                       os='nd',
                       username='admin',
                       password='bad_pw')
        with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to agent-lab11-pm'):
            c.connect()

    def test_bad_connect_for_password_credential(self):
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os nd --state connect_for_password'],
                       os='nd',
                       credentials=dict(default=dict(
                        username='admin', password='bad_pw')))
        with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to agent-lab11-pm'):
            c.connect()

    def test_bad_connect_for_password_credential_no_recovery(self):
        """ Ensure password retry does not happen if a credential fails. """
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os nd --state connect_for_password'],
                       os='nd',
                       credentials=dict(default=dict(
                        username='admin', password='cisco'),
                        bad=dict(username='baduser', password='bad_pw')),
                       login_creds=['bad', 'default'])
        with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to agent-lab11-pm'):
            c.connect()

    def test_bad_connect_for_password_credential_proper_recovery(self):
        """ Test proper way to try multiple device credentials. """
        c = Connection(hostname='agent-lab11-pm',
            start=['mock_device_cli --os nd --state connect_for_password'],
            os='nd',
            credentials=dict(default=dict(
             username='admin', password='cisco'),
             bad=dict(username='baduser', password='bad_pw')),
            login_creds=['bad', 'default'])
        try:
            c.connect()
        except UniconConnectionError:
            c.context.login_creds=['default']
            c.connect()

    def test_bad_connect_for_password_credential_proper_recovery_pyats(self):
        """ Test proper way to try multiple device credentials via pyats. """
        testbed = """
        devices:
          agent-lab11-pm:
            type: nd
            os: nd
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                command: mock_device_cli --os nd --state connect_for_password
                credentials:
                  default:
                    username: admin
                    password: cisco
                  bad:
                    username: admin
                    password: bad_pw
                login_creds: [bad, default]
        """
        tb=loader.load(testbed)
        l = tb.devices['agent-lab11-pm']
        with self.assertRaises(UniconConnectionError):
            l.connect(connection_timeout=20)
        l.destroy()
        l.connect(login_creds=['default'])
        self.assertEqual(l.is_connected(), True)
        l.disconnect()

    def test_connect_for_login_incorrect(self):
        c = Connection(hostname='agent-lab11-pm',
                       start=['mock_device_cli --os nd --state login'],
                       os='nd',
                       username='cisco',
                       password='wrong_password')
        with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to agent-lab11-pm'):
            c.connect()

    def test_connect_hit_enter(self):
        c = Connection(hostname='nd',
                       start=['mock_device_cli --os nd --state hit_enter'],
                       os='nd')
        c.connect()
        c.disconnect()

    def test_connect_timeout(self):
        testbed = """
        devices:
          nd-server:
            type: nd
            os: nd
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                command: mock_device_cli --os nd --state login_ssh_delay
        """
        tb=loader.load(testbed)
        l = tb.devices['nd-server']
        l.connect(connection_timeout=20)
        self.assertEqual(l.is_connected(), True)
        l.disconnect()

    def test_connect_timeout_error(self):
        testbed = """
        devices:
          nd-server:
            type: nd
            os: nd
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                command: mock_device_cli --os nd --state login_ssh_delay
        """
        tb=loader.load(testbed)
        l = tb.devices['nd-server']
        with self.assertRaises(UniconConnectionError) as err:
          l.connect(connection_timeout=0.5)
        l.disconnect()

    def test_connect_passphrase(self):
        testbed = """
        devices:
          nd-server:
            type: nd
            os: nd
            credentials:
              default:
                username: admin
                password: cisco
            connections:
              defaults:
                class: unicon.Unicon
              cli:
                command: mock_device_cli --os nd --state login_passphrase
        """
        tb=loader.load(testbed)
        l = tb.devices['nd-server']
        l.connect()

    def test_connect_connectReply(self):
        c = Connection(hostname='nd',
                       start=['mock_device_cli --os nd --state connect_ssh'],
                       os='nd',
                       username='admin',
                       password='cisco',
                       connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

    def test_connect_admin_prompt(self):
        c = Connection(hostname='nd',
                       start=['mock_device_cli --os nd --state nd_password4'],
                       os='nd',
                       username='admin',
                       password='cisco')
        c.connect()
        c.disconnect()


class TestNDPluginPrompts(unittest.TestCase):
    prompt_cmds = [
      'prompt1',
      'prompt2',
      'prompt3',
      'prompt4',
      'prompt5',
      'prompt6',
      'prompt7',
      'prompt8',
      'prompt9',
      'prompt10',
      'prompt11',
      'prompt12',
      'prompt13',
      'prompt14',
      'prompt15',
      'prompt16',
      'prompt17',
      'prompt18',
      'prompt19'
    ]

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='nd',
                            start=['mock_device_cli --os nd --state exec'],
                            os='nd')
        cls.c.connect()

    def test_connect(self):
        for p in self.prompt_cmds:
            # will raise a timeout error if prompt is not matched
            self.c.execute(p, timeout=15)

    def test_prompt_removal(self):
        for p in self.prompt_cmds:
            self.c.execute(p, timeout=15)
            ls = self.c.execute('ls')
            self.assertEqual(ls.replace('\r', ''), mock_data['exec']['commands']['ls'].strip())


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestLearnHostname(unittest.TestCase):

    def test_learn_hostname(self):
        states = {
          'exec': 'ND',
          'exec2': 'ND',
          'exec3': 'ND',
          'exec4': 'host',
          'exec5': 'agent-lab9-pm',
          'exec6': 'agent-lab11-pm',
          'exec7': 'localhost',
          'exec8': 'vm-7',
          'exec9': 'dev-server',
          'exec10': 'dev-1-name',
          'exec11': 'new-host',
          'exec12': 'host',
          'exec13': 'host',
          'exec14': 'rally',
          'exec15': LinuxSettings().DEFAULT_LEARNED_HOSTNAME,
          'sma_prompt' : 'sma03',
          'sma_prompt_1' : 'pod-esa01',
          'exec18': LinuxSettings().DEFAULT_LEARNED_HOSTNAME,
        }

        for state in states:
            print('\n\n## Testing state %s ##' % state)
            testbed = """
              devices:
                nd:
                  os: nd
                  type: nd
                  tacacs:
                      username: admin
                  passwords:
                      linux: admin
                  connections:
                    defaults:
                      class: unicon.Unicon
                    cli:
                      command: mock_device_cli --os nd --state {state}
                """.format(state=state)
            tb = loader.load(testbed)
            c = tb.devices.nd
            c.connect(learn_hostname=True)
            self.assertEqual(c.learned_hostname, states[state])

            # only check for supported prompts
            if states[state] != LinuxSettings().DEFAULT_LEARNED_HOSTNAME:
                x = c.execute('xml')
                self.assertEqual(x.replace('\r', ''), mock_data['exec']['commands']['xml']['response'].strip())
                x = c.execute('banner1')
                self.assertEqual(x.replace('\r', ''), mock_data['exec']['commands']['banner1']['response'].strip())
                x = c.execute('banner2')
                self.assertEqual(x.replace('\r', ''), mock_data['exec']['commands']['banner2']['response'].strip())

    def test_connect_disconnect_without_learn_hostname(self):
        testbed = """
          devices:
            nd:
              os: nd
              type: nd
              tacacs:
                  username: admin
              passwords:
                  linux: admin
              connections:
                defaults:
                  class: unicon.Unicon
                cli:
                  command: mock_device_cli --os nd --state exec
          """
        tb = loader.load(testbed)
        nd = tb.devices.nd
        nd.connect()
        nd.disconnect()
        nd.connect()

    def test_connect_disconnect_with_learn_hostname(self):
        testbed = """
          devices:
            nd:
              os: nd
              type: nd
              tacacs:
                  username: admin
              passwords:
                  linux: admin
              connections:
                defaults:
                  class: unicon.Unicon
                cli:
                  command: mock_device_cli --os nd --state exec
          """
        tb = loader.load(testbed)
        nd = tb.devices.nd
        nd.connect(learn_hostname=True)
        nd.disconnect()
        # If disconnect is used, learn_hostname will still be used even though not specified.
        nd.connect()


class TestRegexPattern(unittest.TestCase):

    def test_prompt_pattern(self):
        patterns = LinuxPatterns().__dict__
        known_slow_patterns = ['learn_hostname', 'learn_os_prompt']

        slow_patterns = {}

        lines = ("a" * 80 + '\n')*500

        for p in sorted(patterns):
            if p in known_slow_patterns: continue
            regex = patterns[p]
            print("Pattern: {} '{}', ".format(p, regex), end="", flush=True)

            timings = []
            for x in range(3):
                start_time = datetime.datetime.now()
                m = re.search(regex,lines)
                end_time = datetime.datetime.now()
                elapsed_time = end_time - start_time
                us = elapsed_time.microseconds
                print("us: {} ".format(us), end='')
                if us > 2000:
                    timings.append(us)
            print()

            if len(timings) == 3:
                slow_patterns[regex] = timings

        if slow_patterns:
          raise Exception('Slow patterns:\n{}'.format(pformat(slow_patterns)))


class TestPS1PS2(unittest.TestCase):

  def test_ps1_ps2_prompts(self):
      testbed = """
      devices:
        nd-server:
          type: nd
          os: nd
          tacacs:
            username: cisco
          passwords:
            linux: cisco
          connections:
            defaults:
              class: unicon.Unicon
            cli:
              command: mock_device_cli --os nd --state exec_ps1
      """
      from pyats.topology import loader
      tb = loader.load(testbed)
      n = tb.devices['nd-server']
      n.connect(learn_hostname=False)
      r = n.execute('for x in 1 2 3; do\necho $x\ndone')
      self.assertEqual(r, {'for x in 1 2 3; do': '', 'echo $x': '', 'done': '1\r\n2\r\n3'})

class TestNDPluginPing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='nd',
                            start=['mock_device_cli --os nd --state exec'],
                            os='nd')
        cls.c.connect()

    def test_ping_success(self):
        r = self.c.ping('127.0.0.1')
        self.assertEqual(r.replace('\r', ''),
            mock_data['exec']['commands']['ping -A -c5 127.0.0.1']['response'].strip())

    def test_ping_fail(self):
        with self.assertRaises(SubCommandFailure) as err:
          r = self.c.ping('2.2.2.2')
        self.assertEqual(err.exception.args[1][0], '100% packet loss')

    def test_ping_empty_error_pattern(self):
        r = self.c.ping('2.2.2.2', error_pattern=[])
        self.assertEqual(r.replace('\r', ''),
            mock_data['exec']['commands']['ping -A -c5 2.2.2.2']['response'].strip())

    def test_ping_none_error_pattern(self):
        r = self.c.ping('2.2.2.2', error_pattern=None)
        self.assertEqual(r.replace('\r', ''),
            mock_data['exec']['commands']['ping -A -c5 2.2.2.2']['response'].strip())

    def test_ping_fail_custom_error_pattern(self):
        with self.assertRaises(SubCommandFailure) as err:
          r = self.c.ping('127.0.0.1', error_pattern=[' 0% packet loss'])
        self.assertEqual(err.exception.args[1][0], ' 0% packet loss')

    def test_ping_options(self):
        r = self.c.ping('127.0.0.1', options='A')
        self.assertEqual(r.replace('\r', ''),
            mock_data['exec']['commands']['ping -A -c5 127.0.0.1']['response'].strip())

    def test_ping_count(self):
        r = self.c.ping('127.0.0.1', count=10)
        self.assertEqual(r.replace('\r', ''),
            mock_data['exec']['commands']['ping -A -c10 127.0.0.1']['response'].strip())

    def test_ping_no_addr(self):
        with self.assertRaises(SubCommandFailure) as err:
          r = self.c.ping('')
        self.assertEqual(err.exception.args[0], 'Address is not specified')

    def test_ping_invalid_error_pattern(self):
        with self.assertRaises(ValueError) as err:
          r = self.c.ping('127.0.0.1', error_pattern='abc')
        self.assertEqual(err.exception.args[0], 'error pattern must be a list')

    def test_ping_ipv6_addr(self):
        r = self.c.ping('::1')
        self.assertEqual(r.replace('\r', ''),
            mock_data['exec']['commands']['ping6 -A -c5 ::1']['response'].strip())

    def test_ping_unknown_boolean_option(self):
        with self.assertLogs('unicon') as cm:
          r = self.c.ping('127.0.0.1', options='Az')
          self.assertEqual(cm.output, ['WARNING:unicon:'
                            'Uknown ping option - z, ignoring'])

    def test_ping_unknown_arg_option(self):
        with self.assertLogs('unicon') as cm:
          r = self.c.ping('127.0.0.1', x='a')
          self.assertEqual(cm.output, ['WARNING:unicon:'
                            'Uknown ping option - x, ignoring'])


class TestNDPluginTERM(unittest.TestCase):

  def test_nd_TERM(self):
      testbed = """
      devices:
        nd:
          os: nd
          type: nd
          connections:
            defaults:
              class: unicon.Unicon
            vty:
              command: bash
      """
      tb = loader.load(testbed)
      l = tb.devices.nd
      l.connect()
      l.execute('PS1=bash#')
      # forcing the prompt pattern without $
      # echo $TERM is matched as a prompt pattern depending on timing
      l.state_machine.get_state('shell').pattern = r'^(.*?([>~%]|[^#\s]#))\s?$'
      term = l.execute('echo $TERM')
      self.assertEqual(term, l.settings.TERM)

  def test_os_TERM(self):
      testbed = """
      devices:
        nd:
          os: nd
          type: nd
          connections:
            defaults:
              class: unicon.Unicon
            vty:
              command: bash
      """

      tb = loader.load(testbed)
      l = tb.devices.nd
      s = LinuxSettings()
      delattr(s, 'TERM')
      delattr(s, 'ENV')
      l.connect(settings=s)
      l.execute('PS1=bash#')
      # forcing the prompt pattern without $
      # echo $TERM is matched as a prompt pattern depending on timing
      l.state_machine.get_state('shell').pattern = r'^(.*?([>~%]|[^#\s]#))\s?$'
      term = l.execute('echo $TERM')
      self.assertEqual(term, os.environ.get('TERM', 'dumb'))

class TestNDPluginENV(unittest.TestCase):

  def test_nd_ENV(self):
      testbed = """
      devices:
        nd:
          os: nd
          type: nd
          connections:
            defaults:
              class: unicon.Unicon
            vty:
              command: bash
      """
      tb = loader.load(testbed)
      l = tb.devices.nd
      l.connect()
      term = l.execute('echo $TERM')
      self.assertIn(l.settings.ENV['TERM'], term)
      lc = l.execute('echo $LC_ALL')
      self.assertIn(l.settings.ENV['LC_ALL'], lc)
      size = l.execute('stty size')
      self.assertEqual(size, '200 200')


class TestNDPluginExecute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='nd',
                           start=['mock_device_cli --os nd --state exec'],
                           os='nd',
                           credentials={'sudo': {'password': 'sudo_password'}})

        cls.c.connect()

    def test_execute_error_pattern(self):
        with self.assertRaises(SubCommandFailure) as err:
          r = self.c.execute('cd abc')

    def test_multi_thread_execute(self):
        commands = ['ls'] * 10
        with ThreadPoolExecutor(max_workers=10) as executor:
            all_task = [executor.submit(self.c.execute, cmd)
                        for cmd in commands]
            results = [task.result() for task in all_task]

    def test_multi_process_execute(self):
        class Child(multiprocessing.Process):
            pass

        commands = ['ls'] * 3
        processes = [Child(target=self.c.execute, args=(cmd,))
                     for cmd in commands]
        for process in processes:
            process.start()
        for process in processes:
            process.join()

    def test_execute_check_retcode(self):
      self.c.settings.CHECK_RETURN_CODE = True
      with self.assertRaises(SubCommandFailure):
        self.c.execute('cd abc', error_pattern=[], valid_retcodes=[0])

      # second time, the mocked return code is 0
      self.c.execute('ls', error_pattern=[], valid_retcodes=[0])

      # third time, the mocked return code is 2
      self.c.execute('ls', error_pattern=[], valid_retcodes=[2])

      with self.assertRaises(AssertionError):
        # raises assertion because the valid_retcodes is not a list
        self.c.execute('cd abc', error_pattern=[], valid_retcodes=0)

      # return code is 2 (last one in the mock list)
      with self.assertRaises(SubCommandFailure):
        self.c.execute('ls', error_pattern=[])

      self.c.settings.CHECK_RETURN_CODE = False
      # should not raise exception
      self.c.execute('cd abc', error_pattern=[], valid_retcodes=[0])
      # should not have echo $? in the output
      self.assertEqual(self.c.spawn.match.match_output,
                       'cd abc\r\nbash: cd: abc: No such file or directory\r\nND$ ')

      # return code is 2 (last one in the mock list)
      with self.assertRaises(SubCommandFailure):
        self.c.execute('ls', error_pattern=[], check_retcode=True)

      # return code is 2 (last one in the mock list)
      self.c.execute('ls', error_pattern=[], check_retcode=True, valid_retcodes=[0, 2])

    def test_sudo_handler(self):
      self.c.execute('sudo')

      self.c.context.credentials['sudo']['password'] = 'unknown'
      with self.assertRaises(unicon.core.errors.SubCommandFailure):
        self.c.execute('sudo_invalid')

      self.c.context.credentials['sudo']['password'] = 'invalid'
      with self.assertRaises(unicon.core.errors.SubCommandFailure):
        self.c.execute('sudo_invalid')


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestLoginPasswordPrompts(unittest.TestCase):
    def test_custom_user_password_prompt(self):
        c = Connection(hostname='nd',
                       start=['mock_device_cli --os nd --state nd_login3'],
                       os='nd',
                       username='user3',
                       password='cisco')
        c.settings.LOGIN_PROMPT = r'.*Identifier:\s?$'
        c.settings.PASSWORD_PROMPT = r'.*Passe:\s?$'
        c.connect()
        c.disconnect()

    def test_topology_custom_user_password_prompt(self):
        testbed = r"""
          devices:
            nd:
              type: nd
              os: nd
              tacacs:
                username: user3
                login_prompt: '.*Identifier:\s?$'
                password_prompt: '.*Passe:\s?$'
              passwords:
                linux: cisco
              connections:
                defaults:
                  class: unicon.Unicon
                nd:
                  command: 'mock_device_cli --os nd --state nd_login3'
                   """
        t = loader.load(testbed)
        d = t.devices['nd']
        d.connect()
        d.disconnect()

class TestNDPromptOverride(unittest.TestCase):

    def test_override_prompt(self):
        settings = LinuxSettings()
        prompt = 'prompt'
        settings.PROMPT = prompt
        c = Connection(hostname='nd',
                       start=['mock_device_cli --os nd --state exec'],
                       os='nd',
                       settings=settings)
        assert c.state_machine.states[0].pattern == prompt

    def test_override_shell_prompt(self):
        settings = LinuxSettings()
        prompt = 'shell_prompt'
        settings.SHELL_PROMPT = prompt
        c = Connection(hostname='nd',
                       start=['mock_device_cli --os nd --state exec'],
                       os='nd',
                       settings=settings,
                       learn_hostname=True)
        c.connect()
        assert c.state_machine.states[0].pattern == prompt


if __name__ == "__main__":
  unittest.main()

