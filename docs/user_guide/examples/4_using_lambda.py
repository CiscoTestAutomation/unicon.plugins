import os
from unicon.eal.expect import Spawn, TimeoutError
from unicon.eal.dialogs import Statement, Dialog

router_command = os.path.join(os.getcwd(), 'router.sh')
prompt = 'sim-router'
enable_prompt = prompt + '#'
disable_prompt = prompt + '>'

# construct the dialog
d = Dialog([
    [r'enter to continue \.\.\.', lambda spawn: spawn.sendline(), None, True, False],
    [r'username:\s?$', lambda spawn: spawn.sendline("admin"), None, True, False],
    [r'password:\s?$', lambda spawn: spawn.sendline("lab"), None, True, False],
    [disable_prompt, None, None, False, False],
])

s = Spawn(router_command)

# at this stage we are anticipating the program to wait for a new line
d.process(s)
s.close()
