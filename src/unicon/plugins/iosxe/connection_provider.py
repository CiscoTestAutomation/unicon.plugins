
import re
from unicon.eal.dialogs import Dialog
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider
from unicon.plugins.generic.patterns import GenericPatterns
from unicon.statemachine import State
from unicon.plugins.generic.statements import chatty_term_wait
from unicon.plugins.utils import get_device_mode


class IosxeSingleRpConnectionProvider(GenericSingleRpConnectionProvider):
    """ Implements Iosxe singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)


    def learn_tokens(self):
        con = self.connection
        if (not con.learn_tokens or not con.settings.LEARN_DEVICE_TOKENS)\
            and not con.operating_mode:
            # make sure device is in valid unicon state
            con.sendline()
            con.state_machine.go_to('any',
                                    con.spawn,
                                    context=con.context,
                                    prompt_recovery=con.prompt_recovery)
            # If the learn token is not enabled we need to see if the device is in Controller-Managed mode 
            # or it's in autonomous mode. If the device is in Controller-Managed mode, enable token discovery.
            if get_device_mode(con) == 'Controller-Managed':
                # The device is in Controller-Manged mode so we need to learn the abstraction tokens.
                con.overwrite_testbed_tokens = True
                con.learn_tokens = True
                # "operating_mode" attribute is added to the connection object to avoid getting in a loop
                con.operating_mode = True
                # Add learn tokens state to state machine so it can use a looser
                # prompt pattern to match. Required for at least some Linux prompts
                if 'learn_tokens_state' not in [str(s) for s in con.state_machine.states]:
                    self.learn_tokens_state = State('learn_tokens_state',
                                        GenericPatterns().learn_os_prompt)
                    con.state_machine.add_state(self.learn_tokens_state)

                # The first thing we need to is to send stop PnP discovery otherwise device will not execute any command.
                con.spawn.sendline('pnpa service discovery stop')
                # The device may reload after the command we get the dialog statements from reload service and try to handle that
                dialog = con.reload.dialog
                dialog.append(Statement(con.state_machine.get_state('enable').pattern, action=None,
                                        args=None, loop_continue=False, continue_timer=False))
                dialog.process(con.spawn,
                                context=con.context,
                                timeout=con.settings.RELOAD_WAIT,
                                prompt_recovery=con.prompt_recovery)
                # The device may be chatty at this time we need to wait for 
                # it to to settle down.
                chatty_wait_time = con.settings.CONTROLLER_MODE_CHATTY_WAIT_TIME
                chatty_term_wait(con.spawn, trim_buffer=True, wait_time=chatty_wait_time)
                con.sendline()
                con.state_machine.go_to('any',
                                        con.spawn,
                                        context=con.context,
                                        prompt_recovery=con.prompt_recovery)
        super().learn_tokens()

