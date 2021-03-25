import os
from unicon.eal.expect import Spawn, TimeoutError
from unicon.eal.dialogs import Statement, Dialog

router_command = os.path.join(os.getcwd(), 'router.sh')
prompt = 'sim-router'
enable_prompt = prompt + '#'
disable_prompt = prompt + '>'

# callback to send password, we still need this callback 
# because shorthand notation is for handling trivial payloads.
# this function does little more than that.
def send_passwd(spawn, session, enablepw, loginpw):
    if 'flag' not in session:
        # this is first entry hence we need to send login password.
        session.flag = True
        spawn.sendline(loginpw)
    else:
        # if we come here that means it is second entry and here.
        # we need to send the enable password.
        spawn.sendline(enablepw)

# construct the dialog.
# here we see how shorthand notation can make the code look leaner.
d = Dialog([
    [r'enter to continue \.\.\.', 'sendline()', None, True, False],
    [r'username:\s?$', "sendline(admin)", None, True, False],
    [r'password:\s?$', send_passwd, {'enablepw': 'lablab', 'loginpw': 'lab'}, True, False],
    [disable_prompt, 'sendline(enable)', None, True, False],
    [enable_prompt, None, None, False, False],
])

s = Spawn(router_command)

# at this stage we are anticipating the program to wait for a new line
d.process(s)

s.close()
