__author__ = "Ashok Joshi <ashojosh@cisco.com>"
from unicon.plugins.iosxr.connection_provider import IOSXRSingleRpConnectionProvider,IOSXRDualRpConnectionProvider
from unicon.plugins.iosxr.statements import authentication_statement_list
from unicon.plugins.generic.statements import pre_connection_statement_list
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxr.enxr.settings import EnxrSettings
from unicon import log
import traceback
import time
import pexpect

class IOSXREnxrSingleRpConnectionProvider(IOSXRSingleRpConnectionProvider):
    """ Implements EnXR singleRP Connection Provider,
        This class overrides the IOSXRSingleRpConnectionProvider
    """

    def __init__(self, connection):
        super().__init__(connection)
        self.connected = False
        self.ssh = None
        self.get_connection_dialog()

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

    def disconnect(self):
        """Disconnect from EnXR.
        Returns:
          (bool): True if disconnect is successful
        """
        import pdb
        pdb.set_trace()
        try:
            if self.connected:
                self.ssh.close()
                self.connected = False
        except Exception:
            log.error('EnXR disconnect failed %s',
                      self.dev_profile.base.profile_name)
            log.error(traceback.format_exc())
        finally:
            return self.connected