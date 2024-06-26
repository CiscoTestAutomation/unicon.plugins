class StackException(Exception):
    ''' base class '''
    pass

class StackMemberReadyException(StackException):
    """
    Exception for when all the member of stack device is configured
    """
    pass

