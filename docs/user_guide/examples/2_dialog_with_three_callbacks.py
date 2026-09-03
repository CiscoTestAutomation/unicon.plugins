import os
from unicon.eal.expect import Spawn, TimeoutError
from unicon.eal.dialogs import Statement, Dialog

router_command = os.path.join(os.getcwd(), 'router.sh')
prompt = 'sim-router'
enable_prompt = prompt + '#'
disable_prompt = prompt + '>'

# callback to send password
def send_password(spawn, password='lab'):
    spawn.sendline(password)

# callback to send username
def send_username(spawn, username="admin"):
    spawn.sendline(username)

# callback to send new line
def send_new_line(spawn):
    spawn.sendline()

# construct the dialog
d = Dialog([
    [r'enter to continue \.\.\.', send_new_line, None, True, False],
    [r'username:\s?$', send_username, None, True, False],
    [r'password:\s?$', send_password, None, True, False],
    [disable_prompt, None, None, False, False],
])

s = Spawn(router_command)

# at this stage we are anticipating the program to wait for a new line
d.process(s)
s.close()
