import re

from unicon.utils import Utils

class LinuxUtils(Utils):

    def truncate_trailing_prompt(self, con_state, result, hostname=None,
                                 result_match=None):
        # Prompt pattern syntax is different from the generic plugin
        # The regex group match is grouped around the prompt itself
        pattern = con_state.pattern
        match = re.findall(pattern, result, re.MULTILINE)
        if match:
            # get the last prompt pattern match line and replace it with ""
            prompt_line = match[-1]
            if isinstance(prompt_line, tuple):
                prompt_line = prompt_line[0]
            output = result.replace(prompt_line, "")
        else:
            output = result
        return output.strip()
