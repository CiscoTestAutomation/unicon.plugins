
from unicon.bases.routers.services import BaseService


class Tie(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'

    def call_service(self, command=[], target=None, timeout=30, **kwargs):
        handle = self.get_handle(target)
        if command:
            handle.state_machine.go_to('tie', handle.spawn, timeout=timeout)
            self.result = handle.execute(command, timeout=timeout, **kwargs)
        else:
            self.result = self.__class__.ContextMgr(connection=handle, timeout=timeout)

    class ContextMgr(object):
        def __init__(self, connection, timeout=30):
            self.conn = connection
            self.timeout = timeout

        def __enter__(self):
            self.conn.log.info('+++ attaching tie +++')

            self.conn.state_machine.go_to('tie', self.conn.spawn, timeout=self.timeout)

            return self

        def __exit__(self, exc_type, exc_value, exc_tb):
            self.conn.log.info('--- detaching tie ---')

            sm = self.conn.state_machine
            sm.go_to('enable', self.conn.spawn)

            # do not suppress
            return False

        def __getattr__(self, attr):
            if attr in ('execute', 'sendline', 'send', 'expect'):
                return getattr(self.conn, attr)

            raise AttributeError('%s object has no attribute %s'
                                 % (self.__class__.__name__, attr))
