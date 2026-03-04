from unicon.utils import ANSI_REGEX
from unicon.plugins.generic.patterns import GenericPatterns


class LinuxPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()

        self.continue_connect = r'Are you sure you want to continue connecting \(yes/no(/\[fingerprint\])?\)'
        self.hit_enter = r'Hit Enter to proceed:'

        # The reason for using the learn_hostname pattern instead of the shell_prompt pattern
        # to learn the hostname, is that the regex in the router implementation matches \S
        # which is not exact enough for the known linux prompts.
        # Supported prompt formats.
        #   Linux#
        #   Linux>
        #   user@host ~$
        #   [user@host ~]$
        #   agent-lab9-pm:~:2017>
        #   root@agent-lab11-pm:~#
        #   root@localhost ~%
        #   vm-7:3>
        #   \x1b]0;cisco@dev-server:~^Gcisco@dev-server:3>
        #   (dev) user@dev-1-name dir$
        #   [user@new-host dir]$
        #   host ~ #
        #   host:~ #
        #   \x1b]0;rally@rally: /workspace\x07rally@rally:/workspace$ \x1b[K
        #   root@sj21-pxe-03.cisco.com:~/
        #   [Linux] #
        #   cxta@mock-server:~$
        #   (server.cisco.com)~ :
        #   sma03:testuser 1]
        #   pod-esa01.cisco.com:testuser 1]
        #   \x1b[37mapc>
        #   \x1b[0;32m[user@host:~] >\x1b[m \x1b[m\x0f
        self.learn_hostname = r'^.*?({a})?\(?(?P<hostname>[-\w\.]+)\)?\s?([-\w\]/~:\.\d ]+)?([>\$~%#\]]|~/|~\s?:)\s*(\x1b\S+\s?)*$'.format(a=ANSI_REGEX)

        # shell_prompt pattern will be used by the 'shell' state after lean_hostname matches
        # a known hostname pattern this pattern is set for the shell state at transition
        # from learn_hostname to shell, see statemachine for more details.
        # Supported shell prompt formats, %N is replaced with learned hostname.
        #   Linux$
        #   Linux#
        #   Linux>
        #   user@host ~$
        #   [user@host ~]$
        #   agent-lab9-pm:~:2017>
        #   root@agent-lab11-pm:~#
        #   root@localhost ~%
        #   vm-7:3>
        #   \x1b]0;cisco@dev-server:~^Gcisco@dev-server:3>
        #   (dev) user@dev-1-name dir$
        #   [user@new-host dir]$
        #   host ~ #
        #   host:~ #
        #   \x1b]0;rally@rally: /workspace\x07rally@rally:/workspace$ \x1b[K
        #   root@sj21-pxe-03.cisco.com:~/
        #   [Linux] #
        #   cxta@mock-server:~$
        #   (server.cisco.com)~ :
        #   sma03:testuser 1]
        #   pod-esa01.cisco.com:testuser 1]
        #   \x1b[37mapc>
        #   \x1b[0;32m[user@host:~] >\x1b[m \x1b[m\x0f
        self.shell_prompt = r'^(.*?(?P<prompt>((\([-\w\.]+\) |\x1b(?!\[\?2004).*?)?\S+)?\(?%N\)?\s?([-\w\]/~\s:\.\d]+)?([>\$~%#\]]|~/|~\s?:)\s?(\x1b\S+\s?)*))$'

        # default linux prompt with loose matching of the prompt
        # this can result in false prompt matching when output has
        # one of the prompt characters at the end of the line,
        # e.g. XML output or a banner
        # Supported fallback prompt formats.
        #   >
        #   $
        #   ~
        #   %
        #   ]
        #   ] # 
        #   user#
        #   ~ #
        #   ~/
        #   admin:
        #   #
        #   ~#
        #   ~ :
        self.prompt = r'^(.*?([>\$~%\]]|\] # |[^#\s]#|~ #|~/|^admin:|^#|~\s?#\s?|~\s?:)\s?(\x1b\S+\s?)*)$'

        self.trex_console = r'^(.*?)(?P<prompt>trex>\s*)$'
