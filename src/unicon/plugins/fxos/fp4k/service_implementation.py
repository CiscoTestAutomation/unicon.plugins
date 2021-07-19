
from unicon.bases.routers.services import BaseService
from ..service_implementation import Reload as FxosReload


class Reload(FxosReload):

    def pre_service(self, *args, **kwargs):
        self.prompt_recovery = self.connection.prompt_recovery
        if 'prompt_recovery' in kwargs:
            self.prompt_recovery = kwargs.get('prompt_recovery')
        # switch to local-mgmt to execute the reboot command
        self.connection.fxos_mgmt()
