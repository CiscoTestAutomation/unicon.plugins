__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.service_implementation import Copy


class IosXECsr1000vVewlcCopy(Copy):
    def call_service(self, reply=Dialog([]), vrf=None, *args, **kwargs):
        if vrf is not None:
            kwargs['extra_options'] = kwargs.setdefault('extra_options', '') \
                                      + ' vrf {}'.format(vrf)
        super().call_service(reply=reply, *args, **kwargs)
