import os
from unicon.eal.utils import send_message_logging
from unicon.eal.backend.pty_backend import Spawn
from unicon import logs

class MoonshineSpawn(Spawn):
    def send(self, command, *args, **kwargs):
        """ Moonshine requires no os.sync() step in the 'send' method. """
        if not isinstance(command, str):
                command = str(command)
        if self.is_writable():
            if logs.IS_EXPECT_LOG_ENABLED:
                message = "Expect Sending ::  " + repr(command)
                log_info = {'color': 'blue'}
                send_message_logging(message, log_info)
            self.last_sent = command
            ret = os.write(self.fd, str.encode(command))
            return ret
