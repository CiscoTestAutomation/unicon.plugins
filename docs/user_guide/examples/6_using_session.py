import os
from unicon.eal.expect import Spawn, TimeoutError
from unicon.eal.dialogs import Statement, Dialog

router_command = os.path.join(os.getcwd(), 'router.sh')
prompt = 'sim-router'
enable_prompt = prompt + '#'
disable_prompt = prompt + '>'

# callback to send password
def send_passwd(spawn, session, enablepw, loginpw):
    if 'flag' not in session:
        # this is first entry hence we need to send login password.
        session.flag = True
        spawn.sendline(loginpw)
    else:
        # if we come here that means it is second entry and here.
        # we need to send the enable password.
        spawn.sendline(enablepw)

# construct the dialog
d = Dialog([
    [r'enter to continue \.\.\.', lambda spawn: spawn.sendline(), None, True, False],
    [r'username:\s?$', lambda spawn: spawn.sendline("admin"), None, True, False],
    [r'password:\s?$', send_passwd, {'enablepw': 'lablab', 'loginpw': 'lab'}, True, False],
    [disable_prompt, lambda spawn: spawn.sendline("enable"), None, True, False],
    [enable_prompt, None, None, False, False],
])

s = Spawn(router_command)

# at this stage we are anticipating the program to wait for a new line
d.process(s)

s.close()
