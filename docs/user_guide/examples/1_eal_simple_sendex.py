import os
from unicon.eal.expect import Spawn, TimeoutError
router_command = os.path.join(os.getcwd(), 'router.sh')
prompt = 'sim-router'
enable_prompt = prompt + '#'
disable_prompt = prompt + '>'
s = Spawn(router_command)
try:
    s.sendline()
    s.expect([r'username:\s?$', r'login:\s?$'], timeout=5)
    s.sendline('admin')
    s.expect([r'password:\s?$'], timeout=5)
    s.sendline('lab')
    s.expect([disable_prompt])
    s.sendline('enable')
    s.expect([r'password:\s?$'], timeout=5)
    s.sendline('lablab')
    s.expect([enable_prompt])
    s.sendline('show clock')
    s.expect([enable_prompt])
except TimeoutError as err:
    print('errored becuase of timeout')

