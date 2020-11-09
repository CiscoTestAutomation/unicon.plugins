__author__ = "Ashok Joshi <ashojosh@cisco.com>"
<<<<<<< HEAD

import traceback
import pexpect
from unicon.plugins.iosxr.connection_provider import IOSXRSingleRpConnectionProvider
from unicon.plugins.iosxr.enxr.settings import EnxrSettings
from unicon import log

class IOSXREnxrSingleRpConnectionProvider(IOSXRSingleRpConnectionProvider):
=======
from unicon.plugins.iosxr.connection_provider import IOSXRSingleRpConnectionProvider,IOSXRDualRpConnectionProvider
from unicon.plugins.iosxr.statements import authentication_statement_list
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxr.enxr.settings import EnxrSettings
from unicon import log
import traceback
import time
import pexpect

class EnxrSingleRpConnectionProvider(IOSXRSingleRpConnectionProvider):
>>>>>>> edcc7403ef1fc3ce709728b2c86e50dc54ee2453
    """ Implements EnXR singleRP Connection Provider,
        This class overrides the IOSXRSingleRpConnectionProvider
    """

    def __init__(self, connection):
        super().__init__(connection)
        self.connected = False
        self.ssh = None
<<<<<<< HEAD
        self.get_connection_dialog()
        self.spawn = None
        self.prompt = None

=======
>>>>>>> edcc7403ef1fc3ce709728b2c86e50dc54ee2453

    @property
    def connected(self):
        """ Return True if session is connected."""
        return self._connected

    @connected.setter
    def connected(self, is_connected):
        self._connected = is_connected

    def connect(self, **kwargs):
        # con = self.connection
        """Connect to EnXR.
        Args:
        kwargs (dict):
            spawn (str): Spawn parameter for pexpect (default "exec").
            prompt (str): Expect parameter for pexpect (default ":ios#").
        Returns:
        (bool): True if connection is successful
        """
        try:
            self.spawn = kwargs.get('spawn', 'exec')
            self.prompt = kwargs.get('prompt', ':ios#')

            if not self.connected:
                p = pexpect.spawn(self.spawn)
                p.expect(self.prompt, timeout=10)
                self.connected = True
                self.ssh = p
            return 'Connected with %s' % (self.connection.device.name)
        except pexpect.exceptions.TIMEOUT:
            log.error('EnXR connect failed ')
        except Exception:
            log.error('EnXR connect failed ')
            log.error(traceback.format_exc())

<<<<<<< HEAD
=======

>>>>>>> edcc7403ef1fc3ce709728b2c86e50dc54ee2453
    def disconnect(self):
        """Disconnect from EnXR.
        Returns:
          (bool): True if disconnect is successful
        """
<<<<<<< HEAD
        import pdb
        pdb.set_trace()
=======
>>>>>>> edcc7403ef1fc3ce709728b2c86e50dc54ee2453
        try:
            if self.connected:
                self.ssh.close()
                self.connected = False
        except Exception:
            log.error('EnXR disconnect failed %s',
                      self.dev_profile.base.profile_name)
            log.error(traceback.format_exc())
        finally:
<<<<<<< HEAD
            return self.connected
=======
            return self.connected
>>>>>>> edcc7403ef1fc3ce709728b2c86e50dc54ee2453
