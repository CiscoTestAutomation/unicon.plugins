__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.eal.dialogs import Statement
from unicon.plugins.nxos.patterns import NxosPatterns

from .setting import Nxos9kSettings

patterns = NxosPatterns()
settings = Nxos9kSettings()


def boot_image(spawn, context, session):
    session.setdefault('boot_attempt_count', 0)
    if session.get('boot_attempt_count') < settings.MAX_BOOT_ATTEMPTS:
        cmd = 'boot {}'.format(context['image_to_boot']) \
            if 'image_to_boot' in context else ''
        spawn.sendline(cmd)
        session['boot_attempt_count'] += 1
    else:
        err_info = 'Too many failed boot attempts have been detected.' \
            if 'image_to_boot' in context \
            else 'Got loader prompt but image_to_boot parameter was not provided.'
        raise Exception(err_info)


loader = Statement(pattern=patterns.loader_prompt,
                   action=boot_image,
                   args=None,
                   loop_continue=True,
                   continue_timer=False)
