import os
from unicon.eal.backend.pty_backend import Spawn

class MoonshineSpawn(Spawn):
    def send(self, command, *args, **kwargs):
        """ Moonshine requires no os.sync() step in the 'send' method. """
        if not isinstance(command, str):
                command = str(command)
        if self.is_writable():
            msg = ">>> Unicon Sending :: {}".format(repr(command))
            self.log.debug(msg)

            self.last_sent = command
            ret = os.write(self.fd, str.encode(command))
            return ret
