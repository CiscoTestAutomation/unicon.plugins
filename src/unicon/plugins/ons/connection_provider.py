
from unicon.utils import to_plaintext

from unicon.bases.routers.connection_provider \
    import BaseSingleRpConnectionProvider


class OnsSingleRpConnectionProvider(BaseSingleRpConnectionProvider):

    def init_handle(self):
        """ bring device handle to initial state
        """
        con = self.connection
        hostname = con.hostname
        credentials = con.context.get('credentials') or {}
        username = credentials.get('default', {}).get('username', '')
        password = to_plaintext(credentials.get('default', {}).get('password', ''))

        if not username or not password:
            con.log.warning(f'No credentials defined for {hostname}')

        if len(password) > 10:
            con.log.warning('Password is possibly too long')

        con.sendline(f'ACT-USER:{hostname}:{username}:100::{password};')
        output = con.expect('(.*)>\s*$')
        if output and isinstance(output.match_output, str):
            if 'COMPLD' not in output.match_output:
                raise ValueError('Login failed')

        self.connection.goto_enable = False
        super().init_handle()
