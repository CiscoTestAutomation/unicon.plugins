
from ..patterns import IosXEPatterns


class IosXECat9kPatterns(IosXEPatterns):

    def __init__(self):
        super().__init__()
        self.rommon_prompt = r'(.*)switch:\s?$'
        self.boot_interrupt_prompt = r'Preparing to autoboot. \[Press Ctrl-C to interrupt\]'
        self.container_shell_prompt = r'^(.*?)(/(\S+)?)+\s+#\s*$'
        self.container_ssh_prompt = r'^(.*?)(\w+-){6,}.*?[\$#]\s*$'
