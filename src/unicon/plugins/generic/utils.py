""" Generic utilities. """

from collections.abc import Sequence
import re
import time

from unicon.core.errors import SubCommandFailure
from unicon.utils import Utils, AttributeDict


class GenericUtils(Utils):

    def get_redundancy_details(self, connection, timeout=None, who='my'):
        """
        :arg  connection:  device connection object
        :return: device role and redundancy mode of the device
        """
        timeout = timeout or connection.settings.EXEC_TIMEOUT
        redundancy_details = AttributeDict()
        if who == "peer":
            show_red_out = connection.execute("show redundancy sta |  in peer",
                                              timeout=timeout)
        else:
            show_red_out = connection.execute("show redundancy sta |  in my",
                                              timeout=timeout)

        if re.search("ACTIVE|active", show_red_out):
            redundancy_details['role'] = "active"
            redundancy_details['state'] =\
                show_red_out[show_red_out.find('-') + 1:].strip()
        elif re.search("standby|STANDBY", show_red_out):
            redundancy_details['role'] = "standby"
            redundancy_details['state'] =\
                show_red_out[show_red_out.find('-') + 1:].strip()
        elif re.search("DISABLED|disabled", show_red_out):
            redundancy_details['role'] = "disabled"
            redundancy_details['state'] =\
                show_red_out[show_red_out.find('-') + 1:].strip()
        show_red_out = connection.execute(
            "show redundancy sta | inc Redundancy State")
        redundancy_details['mode'] =\
            show_red_out[show_red_out.find("=") + 1:].strip()
        return redundancy_details

    def retry_state_machine_go_to(self,
                                  state_machine,
                                  to_state,
                                  spawn,
                                  retries,
                                  retry_sleep,
                                  context=AttributeDict(),
                                  dialog=None,
                                  timeout=None,
                                  hop_wise=False,
                                  prompt_recovery=False):
        for index in range(retries + 1):
            try:
                state_machine.go_to(to_state,
                                    spawn,
                                    context=context,
                                    dialog=dialog,
                                    timeout=timeout,
                                    hop_wise=hop_wise,
                                    prompt_recovery=prompt_recovery)
                break
            except Exception as err:
                if index == retries:
                    raise SubCommandFailure(err, spawn.buffer)
                time.sleep(retry_sleep)

    def retry_handle_state_machine_go_to(self,
                                         handle,
                                         to_state,
                                         retries,
                                         retry_sleep,
                                         context=AttributeDict(),
                                         dialog=None,
                                         timeout=None,
                                         hop_wise=False,
                                         prompt_recovery=False):
        self.retry_state_machine_go_to(handle.state_machine,
                                       to_state,
                                       handle.spawn,
                                       retries,
                                       retry_sleep,
                                       context=context,
                                       dialog=dialog,
                                       timeout=timeout,
                                       hop_wise=hop_wise,
                                       prompt_recovery=prompt_recovery)

    def flatten_splitlines_command(self, command):
        if isinstance(command, str):
            for item in command.splitlines():
                yield item
        elif isinstance(command, Sequence):
            for item in command:
                yield from self.flatten_splitlines_command(item)
        else:
            raise SubCommandFailure('"command" must be a string'
                                    ' or a list of string')
