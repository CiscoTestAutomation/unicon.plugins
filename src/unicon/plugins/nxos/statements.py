
import re

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import boot_timeout_stmt, authentication_statement_list

from .service_statements import additional_connection_dialog
from .patterns import NxosPatterns

patterns = NxosPatterns()


def boot_image(spawn, context, session):
    if not context.get('boot_prompt_count'):
        context['boot_prompt_count'] = 1
    if context.get('boot_prompt_count') < \
            spawn.settings.MAX_BOOT_ATTEMPTS:
        if "boot_cmd" in context:
            cmd = context.get('boot_cmd')
        elif "image_to_boot" in context:
            cmd = "boot {}".format(context['image_to_boot']).strip()
        elif spawn.settings.FIND_BOOT_IMAGE:
            filesystem = spawn.settings.BOOT_FILESYSTEM if \
                hasattr(spawn.settings, 'BOOT_FILESYSTEM') else 'flash:'
            spawn.buffer = ''
            spawn.sendline('dir {}'.format(filesystem))
            dir_listing = spawn.expect(patterns.loader_prompt).match_output
            boot_file_regex = spawn.settings.BOOT_FILE_REGEX if \
                hasattr(spawn.settings, 'BOOT_FILE_REGEX') else r'(\S+\.bin)'
            m = re.search(boot_file_regex, dir_listing)
            if m:
                boot_image = m.group(1)
                cmd = "boot {}{}".format(filesystem, boot_image)
            else:
                cmd = "boot"
        else:
            cmd = "boot"
        spawn.sendline(cmd)
        context['boot_prompt_count'] += 1
    else:
        raise Exception("Too many failed boot attempts have been detected.")


def boot_prompt_handler(spawn, session, context):
    if spawn.settings.BOOT_INIT_EXEC_COMMANDS:
        for cmd in spawn.settings.BOOT_INIT_EXEC_COMMANDS:
            spawn.sendline(cmd)
            spawn.expect(patterns.boot_prompt)
    if spawn.settings.BOOT_INIT_CONFIG_COMMANDS:
        spawn.sendline('config terminal')
        spawn.expect(patterns.boot_config_prompt)
        for cmd in spawn.settings.BOOT_INIT_CONFIG_COMMANDS:
            spawn.sendline(cmd)
            spawn.expect(patterns.boot_config_prompt)
        spawn.sendline('exit')
        spawn.expect(patterns.boot_prompt)
    spawn.sendline('load-nxos')


boot_prompt_stmt =  Statement(pattern=patterns.boot_prompt,
                              action=boot_prompt_handler,
                              args=None,
                              loop_continue=True,
                              continue_timer=False)


boot_statement_list = [
    boot_timeout_stmt,
] + authentication_statement_list + additional_connection_dialog
