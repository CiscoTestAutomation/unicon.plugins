import re
import time
import logging

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.service_statements import\
    admin_password as admin_password_stmt

from .patterns import IosXEReloadPatterns

log = logging.getLogger(__name__)
p = IosXEReloadPatterns()

def please_reset_handler(spawn, session):
    """ Handles the router asking to be reset before booting. """
    if not session.get("please_reset_seen"):
        spawn.log.debug("The device has asked to be reset.")
        session['please_reset_seen'] = True
        if session.get("rommon_count"):
            # Reset rommon prompt processing state (ignore popped result).
            _ = session.pop('rommon_count')

def rommon_prompt_handler(spawn, session, context):
    """ handles connection refused scenarios
    """
    image = context.get('image')
    cmd = "boot " + image[0] if image else "boot"

    if not session.get("please_reset_seen"):
        if not session.get("rommon_count"):
            # Now boot the image
            spawn.sendline(cmd)
            session['rommon_count'] = 1
        else:
            raise Exception(
                'Rommon prompt encountered unexpectedly'
                ', Maybe golden image does not exist for  % ', str(spawn))
    else:
        if session.get("rommon_count"):

            if session['rommon_count'] == 1:
                # Now reset the device
                spawn.send("reset\r\r")
                session['rommon_count'] += 1

            elif session['rommon_count'] == 2:
                # Set the configuration register to boot directly from flash
                # hereafter, and not boot to rommon.
                spawn.send("confreg 0x1\r")
                session['rommon_count'] += 1

            elif session['rommon_count'] == 3:
                # Now boot the image
                spawn.sendline(cmd)
                session['rommon_count'] += 1
            else:
                raise Exception(
                    'Rommon prompt encountered unexpectedly'
                    ', Maybe golden image does not exist for  % ', str(spawn))
        else:
            # The rommon prompt is seen for the first time since the
            # "Please reset" message was detected.
            # Set the configuration register to 0x0 (boot to rommon) and reset.
            # This is recommended in the platform documentation:
            # http://www.cisco.com/c/en/us/support/docs/routers/4000-platform-integrated-services-routers/200678-Troubleshoot-Cisco-4000-platform-ISR-Stuck.pdf
            spawn.send("confreg 0x0\r")
            session['rommon_count'] = 1

def grub_prompt_handler(spawn, session, context):
    """ handles the grub menu during boot process
    """
    log.info("Finding an entry that includes the string '{}'".
             format(context['boot_image']))
    lines = re.split(r'\s{4,}', spawn.buffer)

    selected_line = None
    desired_line = None

    # Get index for selected_line and desired_line
    for index, line in enumerate(lines):
        if '*' in line:
            selected_line = index
        if context['boot_image'] in line:
            desired_line = index

    if not selected_line or not desired_line:
        raise Exception("Cannot figure out which image to select! "
                        "Debug info:\n"
                        "selected_line: {}\n"
                        "desired_line: {}\n"
                        "lines: {}"
                        .format(selected_line, desired_line, lines))

    log.info("Selecting the entry '{}' now.".format(lines[desired_line]))

    num_lines_to_move = desired_line - selected_line

    # If positive we want to move down the list.
    # If negative we want to move up the list.
    if num_lines_to_move >= 0:
        # '\x1B[B' == <down arrow key>
        key = '\x1B[B'
    else:
        # '\x1B[A' == <up arrow key>
        key = '\x1B[A'

    for _ in range(abs(num_lines_to_move)):
        spawn.send(key)
        time.sleep(0.5)

    spawn.sendline()
    time.sleep(0.5)


# Statement covering when a device asks us to reset it.
please_reset_stmt = \
    Statement(pattern=p.please_reset,
              action=please_reset_handler,
              args=None,
              loop_continue=True,
              continue_timer=False)

rommon_boot_stmt = \
    Statement(pattern=p.rommon_prompt,
              action=rommon_prompt_handler,
              args=None,
              loop_continue=True,
              continue_timer=False)

grub_prompt_stmt = \
    Statement(pattern=p.grub_prompt,
              action=grub_prompt_handler,
              args=None,
              loop_continue=True,
              continue_timer=False)

setup_dialog_stmt = \
    Statement(pattern=p.setup_dialog,
              action='sendline(no)',
              args=None,
              loop_continue=True,
              continue_timer=False)

auto_install_stmt = \
    Statement(pattern=p.autoinstall_dialog,
              action='sendline(yes)',
              args=None,
              loop_continue=True,
              continue_timer=False)

boot_from_rommon_statement_list = [
    please_reset_stmt, rommon_boot_stmt, admin_password_stmt,
    setup_dialog_stmt, auto_install_stmt,
]
