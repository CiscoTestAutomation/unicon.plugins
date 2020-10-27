
from unicon.plugins.generic.patterns import GenericPatterns

class LinuxPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()

        self.continue_connect = r'Are you sure you want to continue connecting \(yes/no(/\[fingerprint\])?\)'
        self.hit_enter = r'Hit Enter to proceed:'

        # The reason for using the learn_hostname pattern instead of the shell_prompt pattern
        # to learn the hostname, is that the regex in the router implementation matches \S 
        # which is not exact enough for the known linux prompts.
        self.learn_hostname = r'^.*?(?P<hostname>[-\w]+)\s?([-\w\]/~:\.\d ]+)?([>\$~%#\]])\s*(\x1b\S+)?$'

        # shell_prompt pattern will be used by the 'shell' state after lean_hostname matches
        # a known hostname pattern this pattern is set for the shell state at transition 
        # from learn_hostname to shell, see statemachine for more details.
        self.shell_prompt = r'^(.*?%N\s?([-\w\]/~\s:\.\d]+)?[>\$~%#\]]\s?(\x1b\S+)?)$'

        # default linux prompt with loose matching of the prompt
        # this can result in false prompt matching when output has
        # one of the prompt characters at the end of the line,
        # e.g. XML output or a banner
        self.prompt = r'^(.*?([>\$~%\]]|[^#\s]#|~ #|~/|^admin:|^#|~\s?#\s?)\s?(\x1b\S+)?)$'
