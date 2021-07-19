import os
from unicon.eal.expect import Spawn, TimeoutError
from unicon.eal.dialogs import Statement, Dialog

router_command = os.path.join(os.getcwd(), 'router.sh')
prompt = 'sim-router'
enable_prompt = prompt + '#'
disable_prompt = prompt + '>'

# callback to send any command or a new line character
def send_command(spawn, command=None):
    if command is not None:
        spawn.sendline(command)
    else:
        spawn.sendline()

# construct the dialog
d = Dialog([
    [r'enter to continue \.\.\.', send_command, None, True, False],
    [r'username:\s?$', send_command, {'command': 'admin'}, True, False],
    [r'password:\s?$', send_command, {'command': 'lab'}, True, False],
    [disable_prompt, None, None, False, False],
])

s = Spawn(router_command)

# at this stage we are anticipating the program to wait for a new line
d.process(s)

s.close()
