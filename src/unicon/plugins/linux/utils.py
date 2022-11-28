import re

from unicon.utils import Utils

class LinuxUtils(Utils):

    def truncate_trailing_prompt(self, con_state, result, hostname=None,
                                 result_match=None):
        # Prompt pattern syntax is different from the generic plugin
        # The regex group match is grouped around the prompt itself
        pattern = con_state.pattern
        output = result

        # logic for updated prompts with named capture group
        match = re.search(pattern, result, re.S)
        if match:
            prompt = match.groupdict().get('prompt')
            if prompt:
                output = result.replace(prompt, "")
                return output.strip()

        # existing logic for patterns without named capture group
        match = re.findall(pattern, result, re.MULTILINE)
        prompt_line = match[-1]
        if isinstance(prompt_line, tuple):
            prompt_line = prompt_line[0]
        output = result.replace(prompt_line, "")

        return output.strip()
