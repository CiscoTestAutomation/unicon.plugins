import datetime
import logging

from unicon.eal.dialogs import Statement
from ..patterns import IosXEPatterns
from ..settings import IosXESettings

logger = logging.getLogger(__name__)
patterns = IosXEPatterns()
settings = IosXESettings()


def boot_from_rommon(statemachine, spawn, context):
    context['boot_start_time'] = datetime.datetime.now()
    context['boot_prompt_count'] = 1
    if context.get('grub_boot_image') is None:
        logger.info('No grub_boot_image specified, will use default')
    else:
        logger.info(f"Using grub_boot_image: {context['grub_boot_image']}")
    logger.info('Sending escape to trigger boot menu in GRUB')
    # C8KV uses GRUB as its bootloader rather than traditional ROMMON.
    # Sending ESC interrupts the GRUB autoboot countdown and presents
    # the boot menu, allowing selection of a specific boot image.
    spawn.send('\x1b')


def send_escape(spawn, session):
    session.setdefault('boot_attempt_count', 0)
    if session.get('boot_attempt_count') < settings.MAX_BOOT_ATTEMPTS:
        spawn.send('\x1b')  # send escape character to trigger boot menu in GRUB
        session['boot_attempt_count'] += 1
    else:
        err_info = 'Too many failed boot attempts have been detected.'
        raise Exception(err_info)


# Create c8kv specific boot from rommon statement
# C8KV is a virtual platform that exclusively uses
# GRUB bootloader - the ROMMON prompt is always grub>,
# never the classic rommon> or switch: prompts.
boot_from_rommon_stmt = Statement(
    pattern=patterns.rommon_prompt,
    action=send_escape,
    args=None,
    loop_continue=True,
    continue_timer=False
)
