__author__ = "Syed Raza <syedraza@cisco.com>"


class RpNotRunningError(Exception):
    """ Raise when RP/LC are not in running state after doing a show controller dpc rm dpa """ 
    pass
