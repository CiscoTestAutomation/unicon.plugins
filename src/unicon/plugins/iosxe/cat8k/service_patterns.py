__author__ = "Lukas McClelland <lumcclel@cisco.com>"

class SwitchoverPatterns:
    def __init__(self):
        self.save_config = r'.*System configuration has been modified\.\s*Save\?\s*\[yes\/no\]:\s*$'
        self.build_config= r'Building configuration'
        self.prompt_switchover = r'Proceed with switchover to standby RP\? \[confirm\]\s*$'
        self.switchover_complete = r'console active.\s+Press RETURN to get started!?'
