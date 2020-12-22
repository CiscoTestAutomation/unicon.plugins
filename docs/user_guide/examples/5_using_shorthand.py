import os
from unicon.eal.expect import Spawn, TimeoutError
from unicon.eal.dialogs import Statement, Dialog

router_command = os.path.join(os.getcwd(), 'router.sh')
prompt = 'sim-router'
enable_prompt = prompt + '#'
disable_prompt = prompt + '>'

# construct the dialog
# we can see how shorthand notation makes the code look even more leaner.
d = Dialog([
    [r'enter to continue \.\.\.', 'sendline()', None, True, False],
    [r'username:\s?$', 'sendline(admin)', None, True, False],
    [r'password:\s?$', 'sendline(lab)', None, True, False],
    [disable_prompt, None, None, False, False],
])

s = Spawn(router_command)

# at this stage we are anticipating the program to wait for a new line
d.process(s)
s.close()
