'''
Author: Renato Almeida de Oliveira
Contact: renato.almeida.oliveira@gmail.com
https://twitter.com/ORenato_Almeida
https://www.youtube.com/c/RenatoAlmeidadeOliveira
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.eal.dialogs import Statement
from unicon.plugins.hp_comware.patterns import HPComwarePatterns

from time import sleep

patterns = HPComwarePatterns()


def send_response(spawn, response=""):
    sleep(0.5)
    spawn.sendline(response)


save_confirm = Statement(pattern=patterns.save_confirm,
                         action=send_response, args={'response': 'Y'},
                         loop_continue=True,
                         continue_timer=False)

save_overwrite = Statement(pattern=patterns.overwrite,
                         action=send_response, args={'response': 'Y'},
                         loop_continue=True,
                         continue_timer=False)

file_path = Statement(pattern=patterns.file_save,
                    action='sendline()',
                    loop_continue=True,
                    continue_timer=False)
