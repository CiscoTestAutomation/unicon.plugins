"""
Module:
    unicon.plugins.generic

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining all Services Statement, handlers(callback) and Statement
    list for service dialog would be defined here.
"""

from time import sleep

from unicon.eal.dialogs import Statement
from unicon.core.errors import (SubCommandFailure, CopyBadNetworkError, )

from unicon.plugins.generic.service_patterns import ReloadPatterns, \
    PingPatterns, TraceroutePatterns, CopyPatterns, HaReloadPatterns, \
    SwitchoverPatterns, ResetStandbyPatterns

from .statements import GenericStatements, chatty_term_wait, update_context

from unicon.plugins.utils import (get_current_credential,
    common_cred_username_handler, common_cred_password_handler, )

from unicon.utils import to_plaintext


generic_statements = GenericStatements()

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#           Service handlers
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


def send_response(spawn, response=""):
    chatty_term_wait(spawn)
    spawn.sendline(response)


def send_no_callback(spawn):
    sleep(0.5)
    spawn.sendline("n")


def send_yes_callback(spawn):
    sleep(0.5)
    spawn.sendline("y")


def escape_char_callback(spawn):
    sleep(0.5)
    spawn.sendline()

def login_handler(spawn, context, session):
    """ handles login prompt
    """
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_username_handler(
            spawn=spawn, context=context, credential=credential)
    else:
        if context.get('tacacs_username'):
            spawn.sendline(context['tacacs_username'])
        elif context.get('username'):
            spawn.sendline(context['username'])
        else:
            raise SubCommandFailure("There is no information available about "
                "username/tacacs_username")
        session['tacacs_login'] = 1


def password_handler(spawn, context, session):
    """ handles password prompt
    """
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(
            spawn=spawn, context=context, credential=credential,
            session=session)
    else:
        if session.get('tacacs_login') == 1:
            spawn.sendline(context['tacacs_password'])
            session['tacacs_login'] = 0
        else:
            spawn.sendline(context['enable_password'])

def send_admin_password(spawn, context, session):
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(
            spawn=spawn, context=context, credential=credential,
            session=session, reuse_current_credential=True)
    else:
        if context.get('tacacs_login') == 1:
            spawn.sendline(context['tacacs_password'])
            session['tacacs_login'] = 0
        else:
            spawn.sendline(context['enable_password'])

# TODO check this
def unknown_protocol_handler():
    raise SubCommandFailure("Requested protocol was not running during ping")


def ping_loop_message_handler():
    raise SubCommandFailure("Error while Executing ping command")


def ping_handler(spawn, context, send_key):
    if context.get(send_key):
        spawn.sendline(context[send_key])
    else:
        spawn.sendline()


def ping_handler_1(spawn, context, send_key):
    spawn.sendline(context[send_key])


def send_multicast(spawn, context):
    if context.get('multicast'):
        spawn.sendline(context['multicast'])
    else:
        raise SubCommandFailure("No multicast address specified")


def send_interval_handler(spawn, context):
    if context.get('send_interval'):
        spawn.sendline(context['send_interval'])
    else:
        spawn.sendline("0")


def copy_handler(spawn, context, send_key):
    if context.get(send_key):
        spawn.sendline(context[send_key])
    else:
        spawn.sendline()


def copy_handler_1(spawn, context, send_key):
    if context.get(send_key):
        spawn.sendline(context[send_key])
    else:
        raise SubCommandFailure("%s is not specified" % context[send_key])


def copy_error_handler(context, retry=False):
    if retry:
        raise CopyBadNetworkError("Copy bad network or connectivity message found: %s"
                              % copy_retry_message.pattern)
    else:
        raise SubCommandFailure("Copy error message found :  %s"
                                % copy_error_message.pattern)


def copy_partition_handler(spawn, context):
    if context['partition'] == "0":
        spawn.sendline()
    else:
        spawn.sendline(context[partition])


def copy_dest_handler(spawn, context):
    if context['dest_file'] == "":
        spawn.sendline()
    else:
        spawn.sendline(context['dest_file'])


def copy_dest_directory_handler(spawn, context):
    if context['dest_directory'] == '':
        spawn.sendline()
    else:
        spawn.sendline(context['dest_directory'])


def handle_poap_prompt(spawn, session):
    if 'poap_flag' not in session:
        session.poap_flag = True
        spawn.sendline('y')

def switchover_failure(error):
    raise SubCommandFailure("Switchover Failed with error %s" % error)

def reset_failure(error):
    raise SubCommandFailure("reset_standby_rp Failed with error %s" % error)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Reload  Statements
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

pat = ReloadPatterns()

save_env = Statement(pattern=pat.savenv,
                     action=send_response, args={'response': 'n'},
                     loop_continue=True,
                     continue_timer=False)

confirm_reset = Statement(pattern=pat.confirm_reset,
                          action=send_response, args={'response': 'y'},
                          loop_continue=True,
                          continue_timer=False)

reload_confirm = Statement(pattern=pat.reload_confirm,
                           action=send_response, args={'response': 'yes'},
                           loop_continue=True,
                           continue_timer=False)

reload_confirm_ios = Statement(pattern=pat.reload_confirm_ios,
                               action=send_response, args={'response': ''},
                               loop_continue=True,
                               continue_timer=False)

useracess = Statement(pattern=pat.useracess,
                      action=None, args=None,
                      loop_continue=True,
                      continue_timer=False)

press_enter = Statement(pattern=pat.press_enter,
                        action=send_response, args={'response': ''},
                        loop_continue=False,
                        continue_timer=False)

confirm_config = Statement(pattern=pat.confirm_config,
                           action=send_response, args={'response': ''},
                           loop_continue=True,
                           continue_timer=False)

setup_dialog = Statement(pattern=pat.setup_dialog,
                         action=send_response, args={'response': 'n'},
                         loop_continue=True,
                         continue_timer=False)

auto_install_dialog = Statement(pattern=pat.autoinstall_dialog,
                                action=send_response, args={'response': 'y'},
                                loop_continue=True,
                                continue_timer=False)

module_reload = Statement(pattern=pat.module_reload,
                          action=send_response, args={'response': 'n'},
                          loop_continue=True,
                          continue_timer=False)

save_module_cfg = Statement(pattern=pat.save_module_cfg,
                            action=send_response, args={'response': 'n'},
                            loop_continue=True,
                            continue_timer=False)

reboot_confirm = Statement(pattern=pat.reboot_confirm,
                           action=send_response, args={'response': 'y'},
                           loop_continue=True,
                           continue_timer=False)

secure_passwd_std = Statement(pattern=pat.secure_passwd_std,
                              action=send_response, args={'response': 'n'},
                              loop_continue=True,
                              continue_timer=False)

admin_password = Statement(pattern=pat.admin_password,
                           action=send_admin_password, args=None,
                           loop_continue=True,
                           continue_timer=False)

auto_provision = Statement(pattern=pat.auto_provision,
                           action=handle_poap_prompt, args=None,
                           loop_continue=True,
                           continue_timer=False)

login_stmt = Statement(pattern=pat.username,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=False)

password_stmt = Statement(pattern=pat.password,
                          action=password_handler,
                          args=None,
                          loop_continue=False,
                          continue_timer=False)

connection_closed = Statement(pattern=pat.connection_closed,
                              action=update_context,
                              args={'console': False},
                              loop_continue=False,
                              continue_timer=False)

reload_statement_list = [save_env, confirm_reset, reload_confirm,
                         reload_confirm_ios, press_enter, useracess,
                         confirm_config, setup_dialog, auto_install_dialog,
                         module_reload, save_module_cfg, reboot_confirm,
                         secure_passwd_std, admin_password, auto_provision,
                         login_stmt, password_stmt,
                         generic_statements.password_ok_stmt,
                        ]

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Ping Statements
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

pat = PingPatterns()

ping_loop_message = Statement(pattern=pat.ping_loop_message,
                              action=ping_loop_message_handler, args=None,
                              loop_continue=False,
                              continue_timer=False)

unkonwn_protocol = Statement(pattern=pat.unkonwn_protocol,
                             action=unknown_protocol_handler, args=None,
                             loop_continue=False,
                             continue_timer=False)

protocol = Statement(pattern=pat.protocol,
                     action=ping_handler, args={'send_key': 'proto'},
                     loop_continue=True,
                     continue_timer=False)

transport = Statement(pattern=pat.transport,
                      action=ping_handler, args={'send_key': 'transport'},
                      loop_continue=True,
                      continue_timer=False)

mask = Statement(pattern=pat.mask,
                 action=ping_handler, args={'send_key': 'mask'},
                 loop_continue=True,
                 continue_timer=False)

address = Statement(pattern=pat.address,
                    action=ping_handler_1,
                    args={'send_key': 'addr'},
                    loop_continue=True,
                    continue_timer=False)

vcid = Statement(pattern=pat.vcid,
                 action=ping_handler, args={'send_key': 'vcid'},
                 loop_continue=True,
                 continue_timer=False)

tunnel = Statement(pattern=pat.tunnel,
                   action=ping_handler, args={'send_key': 'tunnel'},
                   loop_continue=True,
                   continue_timer=False)

repeat = Statement(pattern=pat.repeat,
                   action=ping_handler, args={'send_key': 'count'},
                   loop_continue=True,
                   continue_timer=False)

size = Statement(pattern=pat.size,
                 action=ping_handler, args={'send_key': 'size'},
                 loop_continue=True,
                 continue_timer=False)

verbose = Statement(pattern=pat.verbose,
                    action=ping_handler, args={'send_key': 'verbose'},
                    loop_continue=True,
                    continue_timer=False)

interval = Statement(pattern=pat.interval,
                     action=send_interval_handler, args=None,
                     loop_continue=True,
                     continue_timer=False)

packet_timeout = Statement(pattern=pat.packet_timeout,
                           action=ping_handler,
                           args={'send_key': 'ping_packet_timeout'},
                           loop_continue=True,
                           continue_timer=False)

sending_interval = Statement(pattern=pat.sending_interval,
                             action=ping_handler,
                             args={'send_key': 'send_interval'},
                             loop_continue=True,
                             continue_timer=False)

# Check output interface default value
output_interface = Statement(pattern=pat.output_interface,
                             action=ping_handler, args={'send_key': 'oif'},
                             loop_continue=True,
                             continue_timer=False)

novell_echo_type = Statement(pattern=pat.novell_echo_type,
                             action=ping_handler_1,
                             args={'send_key': 'novell_type'},
                             loop_continue=True,
                             continue_timer=False)

vrf = Statement(pattern=pat.vrf,
                action=ping_handler, args={'send_key': 'vrf'},
                loop_continue=True,
                continue_timer=False)

ext_cmds = Statement(pattern=pat.ext_cmds,
                     action=ping_handler,
                     args={'send_key': 'extd_ping'},
                     loop_continue=True,
                     continue_timer=False)
ipv6_source = Statement(pattern=pat.ipv6_source,
                        action=ping_handler,
                        args={'send_key': 'src_addr'},
                        loop_continue=True,
                        continue_timer=False)

ipv6_udp = Statement(pattern=pat.ipv6_udp,
                     action=ping_handler,
                     args={'send_key': 'udp'},
                     loop_continue=True,
                     continue_timer=False)

ipv6_priority = Statement(pattern=pat.ipv6_priority,
                          action=ping_handler,
                          args={'send_key': ''},
                          loop_continue=True,
                          continue_timer=False)

ipv6_verbose = Statement(pattern=pat.ipv6_verbose,
                         action=ping_handler,
                         args={'send_key': 'verbose'},
                         loop_continue=True,
                         continue_timer=False)

ipv6_precedence = Statement(pattern=pat.ipv6_precedence,
                            action=ping_handler,
                            args={'send_key': 'precedence'},
                            loop_continue=True,
                            continue_timer=False)

ipv6_dscp = Statement(pattern=pat.ipv6_dscp,
                      action=ping_handler,
                      args={'send_key': 'dscp'},
                      loop_continue=True,
                      continue_timer=False)

ipv6_hop = Statement(pattern=pat.ipv6_hop,
                     action=ping_handler,
                     args={'send_key': 'ipv6_hbh_headers'},
                     loop_continue=True,
                     continue_timer=False)

pv6_dest = Statement(pattern=pat.pv6_dest,
                     action=ping_handler,
                     args={'send_key': 'ipv6_dst_headers'},
                     loop_continue=False,
                     continue_timer=False)

ipv6_extn_header = Statement(pattern=pat.ipv6_extn_header,
                             action=ping_handler,
                             args={'send_key': 'ipv6_ext_headers'},
                             loop_continue=False,
                             continue_timer=False)

#############################################################################
# Extended Ping Statement
#############################################################################

dest_start = Statement(pattern=pat.dest_start,
                       action=ping_handler,
                       args={'send_key': 'dest_start'},
                       loop_continue=True,
                       continue_timer=False)

interface = Statement(pattern=pat.interface,
                      action=ping_handler,
                      args={'send_key': 'int'},
                      loop_continue=True,
                      continue_timer=False)

dest_end = Statement(pattern=pat.dest_end,
                     action=ping_handler,
                     args={'send_key': 'dest_end'},
                     loop_continue=True,
                     continue_timer=False)

increment = Statement(pattern=pat.increment,
                      action=ping_handler,
                      args={'send_key': 'dest_inc'},
                      loop_continue=True,
                      continue_timer=False)

mpls_header = Statement(pattern=pat.mpls_header,
                        action=ping_handler,
                        args={'send_key': 'exp'},
                        loop_continue=True,
                        continue_timer=False)
tlv_pattern = Statement(pattern=pat.tlv_pattern,
                        action=ping_handler,
                        args={'send_key': 'pad'},
                        loop_continue=True,
                        continue_timer=False)
ttl = Statement(pattern=pat.ttl,
                action=ping_handler,
                args={'send_key': 'ttl'},
                loop_continue=True,
                continue_timer=False)

reply_mode = Statement(pattern=pat.reply_mode,
                       action=ping_handler,
                       args={'send_key': 'reply_mode'},
                       loop_continue=True,
                       continue_timer=False)

revision = Statement(pattern=pat.revision,
                     action=ping_handler,
                     args={'send_key': 'lsp_ping_trace_rev'},
                     loop_continue=True,
                     continue_timer=False)

null_label = Statement(pattern=pat.null_label,
                       action=ping_handler,
                       args={'send_key': 'force_exp_null_label'},
                       loop_continue=True,
                       continue_timer=False)

dscp_header = Statement(pattern=pat.dscp_header,
                        action=ping_handler,
                        args={'send_key': 'dscp'},
                        loop_continue=True,
                        continue_timer=False)

verbomode = Statement(pattern=pat.verbomode,
                      action=ping_handler,
                      args={'send_key': 'verbose'},
                      loop_continue=True,
                      continue_timer=False)

ext_cmds_source = Statement(pattern=pat.ext_cmds_source,
                            action=ping_handler,
                            args={'send_key': 'src_addr'},
                            loop_continue=True,
                            continue_timer=False)

tos = Statement(pattern=pat.tos,
                action=ping_handler,
                args={'send_key': 'tos'},
                loop_continue=True,
                continue_timer=False)

validate = Statement(pattern=pat.validate,
                     action=ping_handler,
                     args={'send_key': 'validate_reply_data'},
                     loop_continue=True,
                     continue_timer=False)

data_pattern = Statement(pattern=pat.data_pattern,
                         action=ping_handler,
                         args={'send_key': 'data_pat'},
                         loop_continue=True,
                         continue_timer=False)

dfbit_header = Statement(pattern=pat.dfbit_header,
                         action=ping_handler,
                         args={'send_key': 'df_bit'},
                         loop_continue=True,
                         continue_timer=False)

dscp = Statement(pattern=pat.dscp,
                 action=ping_handler,
                 args={'send_key': 'dscp'},
                 loop_continue=True,
                 continue_timer=False)

qos = Statement(pattern=pat.qos,
                action=ping_handler,
                args={'send_key': ''},
                loop_continue=True,
                continue_timer=False)

packet = Statement(pattern=pat.packet,
                   action=ping_handler,
                   args={'send_key': ''},
                   loop_continue=True,
                   continue_timer=False)

####################################################################
# Traceroute Statements
####################################################################

tr_pat = TraceroutePatterns()
tr_ingress = Statement(pattern=tr_pat.ingress,
                       action=ping_handler,
                       args={'send_key': 'ingress'},
                       loop_continue=True,
                       continue_timer=False)

tr_source = Statement(pattern=tr_pat.source_address_interface,
                      action=ping_handler,
                      args={'send_key': 'source'},
                      loop_continue=True,
                      continue_timer=False)

tr_target = Statement(pattern=tr_pat.target,
                      action=ping_handler,
                      args={'send_key': 'addr'},
                      loop_continue=True,
                      continue_timer=False)

tr_dscp = Statement(pattern=tr_pat.dscp,
                    action=ping_handler,
                    args={'send_key': 'dscp'},
                    loop_continue=True,
                    continue_timer=False)

tr_numeric = Statement(pattern=tr_pat.numeric_display,
                       action=ping_handler,
                       args={'send_key': 'numeric'},
                       loop_continue=True,
                       continue_timer=False)

tr_timeout = Statement(pattern=tr_pat.timeout_seconds,
                       action=ping_handler,
                       args={'send_key': 'timeout'},
                       loop_continue=True,
                       continue_timer=False)

tr_probe = Statement(pattern=tr_pat.probe_count,
                     action=ping_handler,
                     args={'send_key': 'probe'},
                     loop_continue=True,
                     continue_timer=False)

tr_minimum_ttl = Statement(pattern=tr_pat.minimum_ttl,
                           action=ping_handler,
                           args={'send_key': 'minimum_ttl'},
                           loop_continue=True,
                           continue_timer=False)

tr_maximum_ttl = Statement(pattern=tr_pat.maximum_ttl,
                           action=ping_handler,
                           args={'send_key': 'maximum_ttl'},
                           loop_continue=True,
                           continue_timer=False)

tr_port = Statement(pattern=tr_pat.port_number,
                           action=ping_handler,
                           args={'send_key': 'port'},
                           loop_continue=True,
                           continue_timer=False)

tr_style = Statement(pattern=tr_pat.style,
                     action=ping_handler,
                     args={'send_key': 'style'},
                     loop_continue=True,
                     continue_timer=False)

tr_resolve_as_number = Statement(pattern=tr_pat.resolve_as_number,
                       action=ping_handler,
                       args={'send_key': 'resolve_as_number'},
                       loop_continue=True,
                       continue_timer=False)

trace_route_dialog_list = [unkonwn_protocol, protocol, tr_target, tr_ingress,
                           tr_source, tr_numeric, tr_dscp, tr_timeout,
                           tr_probe, tr_minimum_ttl, tr_maximum_ttl, tr_port,
                           tr_style, tr_resolve_as_number]

####################################################################
# Sweep Related Statement
####################################################################

sweep_range = Statement(pattern=pat.range,
                        action=ping_handler,
                        args={'send_key': 'sweep_ping'},
                        loop_continue=True,
                        continue_timer=False)

range_min = Statement(pattern=pat.range_min,
                      action=ping_handler,
                      args={'send_key': 'sweep_min'},
                      loop_continue=True,
                      continue_timer=False)

range_max = Statement(pattern=pat.range_max,
                      action=ping_handler,
                      args={'send_key': 'sweep_max'},
                      loop_continue=True,
                      continue_timer=False)

range_interval = Statement(pattern=pat.range_interval,
                           action=ping_handler,
                           args={'send_key': 'sweep_interval'},
                           loop_continue=True,
                           continue_timer=False)

others = Statement(pattern=pat.others,
                   action=send_response,
                   args={'response': ''},
                   loop_continue=True,
                   continue_timer=False)

extended_ping_dialog_list = [unkonwn_protocol, protocol, transport, mask,
                             address, vcid, tunnel, repeat, size, verbose,
                             interval, packet_timeout, sending_interval,
                             output_interface, novell_echo_type, vrf, ext_cmds,
                             sweep_range, range_interval, range_max, range_min,
                             dest_start, interface, dest_end, increment,
                             mpls_header, tlv_pattern, ttl, reply_mode,
                             revision, null_label, dscp_header,
                             verbomode, ext_cmds_source, ext_cmds, tos,
                             validate, data_pattern, dfbit_header, dscp,
                             qos, packet, others]

# TODO include ping_loop_message in dialog
ping_dialog_list = [unkonwn_protocol, protocol, transport, mask,
                    address, vcid, tunnel, repeat, size, verbose, interval,
                    packet_timeout, sending_interval, output_interface,
                    novell_echo_type, vrf, ext_cmds, sweep_range, range_interval,
                    range_max, range_min, verbomode, others]

ping6_statement_list = [unkonwn_protocol, ipv6_source, ipv6_udp, ipv6_priority,
                        ipv6_verbose, ipv6_precedence, ipv6_dscp, ipv6_hop,
                        pv6_dest, ipv6_extn_header, protocol, transport, mask,
                        address, vcid, tunnel, repeat, size, verbose, interval,
                        packet_timeout, sending_interval, output_interface,
                        novell_echo_type, vrf, ext_cmds, sweep_range,
                        range_interval, range_max, range_min, dest_start,
                        interface, dest_end, increment, mpls_header,
                        tlv_pattern, ttl, reply_mode, revision, null_label,
                        dscp_header, verbomode, ext_cmds_source, ext_cmds, tos,
                        validate, data_pattern, dfbit_header, dscp, qos, packet,
                        others]

# TODO  extd_LSRTV_cmd_process  implementation

#############################################################################
# Copy Command  Statement
#############################################################################
pat = CopyPatterns()

source_filename = Statement(pattern=pat.source_filename,
                            action=copy_handler,
                            args={'send_key': 'source_file'},
                            loop_continue=True,
                            continue_timer=True)

copy_file = Statement(pattern=pat.copy_file,
                      action=copy_handler,
                      args={'send_key': 'source_file'},
                      loop_continue=True,
                      continue_timer=True)

src_file = Statement(pattern=pat.src_file,
                     action=copy_handler,
                     args={'send_key': 'source_file'},
                     loop_continue=True,
                     continue_timer=True)

hostname = Statement(pattern=pat.hostname,
                     action=copy_handler_1,
                     args={'send_key': 'server'},
                     loop_continue=True,
                     continue_timer=True)

host = Statement(pattern=pat.hostname,
                 action=copy_handler_1,
                 args={'send_key': 'server'},
                 loop_continue=True,
                 continue_timer=True)

nx_hostname = Statement(pattern=pat.nx_hostname,
                        action=copy_handler_1,
                        args={'send_key': 'server'},
                        loop_continue=True,
                        continue_timer=True)

partition = Statement(pattern=pat.partition,
                      action=copy_partition_handler,
                      args=None,
                      loop_continue=True,
                      continue_timer=True)

config = Statement(pattern=pat.config,
                   action=copy_handler,
                   args={'send_key': 'source_file'},
                   loop_continue=True,
                   continue_timer=True)

writeto = Statement(pattern=pat.writeto,
                    action=copy_dest_handler,
                    args=None,
                    loop_continue=True,
                    continue_timer=True)

file_to_write = Statement(pattern=pat.file_to_write,
                          action=copy_dest_handler,
                          args=None,
                          loop_continue=True,
                          continue_timer=True)

username = Statement(pattern=pat.username,
                     action=copy_handler,
                     args={'send_key': 'user'},
                     loop_continue=True,
                     continue_timer=True)

password = Statement(pattern=pat.password,
                     action=copy_handler,
                     args={'send_key': 'password'},
                     loop_continue=True,
                     continue_timer=True)

erase_before_copy = Statement(pattern=pat.erase_before_copy,
                              action=copy_handler_1,
                              args={'send_key': 'erase'},
                              loop_continue=True,
                              continue_timer=True)

net_type = Statement(pattern=pat.net_type,
                     action=copy_handler_1,
                     args={'send_key': 'net_type'},
                     loop_continue=True,
                     continue_timer=True)

copy_confirm = Statement(pattern=pat.copy_confirm,
                         action=send_response,
                         args={'response': ''},
                         loop_continue=True,
                         continue_timer=True)

memory = Statement(pattern=pat.memory,
                   action=send_response,
                   args={'response': ''},
                   loop_continue=True,
                   continue_timer=True)

copy_confirm_1 = Statement(pattern=pat.copy_confirm_1,
                           action=send_response,
                           args={'response': ''},
                           loop_continue=True,
                           continue_timer=True)

copy_confirm_yes = Statement(pattern=pat.copy_confirm_yesno,
                             action=send_response,
                             args={'response': 'yes'},
                             loop_continue=True,
                             continue_timer=True)

copy_reconfirm = Statement(pattern=pat.copy_reconfirm,
                           action=send_response,
                           args={'response': 'yes'},
                           loop_continue=True,
                           continue_timer=True)

copy_progress = Statement(pattern=pat.copy_progress,
                          action=None,
                          args=None,
                          loop_continue=True,
                          continue_timer=False)

rcp_confirm = Statement(pattern=pat.rcp_confirm,
                        action=send_response,
                        args={'response': 'yes'},
                        loop_continue=True,
                        continue_timer=True)
# Recheck this
copy_overwrite = Statement(pattern=pat.copy_overwrite,
                           action=send_response,
                           args={'response': 'y'},
                           loop_continue=True,
                           continue_timer=True)

copy_nx_vrf = Statement(pattern=pat.copy_nx_vrf,
                        action=copy_handler_1,
                        args={'send_key': 'vrf'},
                        loop_continue=True,
                        continue_timer=True)

copy_proceed = Statement(pattern=pat.copy_proceed,
                         action=send_response,
                         args={'response': ''},
                         loop_continue=True,
                         continue_timer=True)

tftp_addr = Statement(pattern=pat.tftp_addr,
                      action=copy_handler,
                      args={'send_key': 'server'},
                      loop_continue=True,
                      continue_timer=True)

copy_complete = Statement(pattern=pat.copy_complete,
                          action=None,
                          args=None,
                          loop_continue=False,
                          continue_timer=False)

# Set loop_continue to True to ensure dialog waits for copy to complete.
copy_error_message = Statement(pattern=pat.copy_error_message,
                               action=copy_error_handler,
                               args=None,
                               loop_continue=False,
                               continue_timer=False)

copy_retry_message = Statement(pattern=pat.copy_retry_message,
                               action=copy_error_handler,
                               args={'retry': True},
                               loop_continue=False,
                               continue_timer=False)

copy_continue = Statement(pattern=pat.copy_continue,
                          action=send_response,
                          args={'response': 'yes'},
                          loop_continue=True,
                          continue_timer=True)

copy_other = Statement(pattern=pat.copy_other,
                       action=send_response,
                       args={'response': 'yes'},
                       loop_continue=True,
                       continue_timer=True)

dest_file = Statement(pattern=pat.dest_file,
                      action=copy_dest_handler,
                      args=None,
                      loop_continue=True,
                      continue_timer=True)

dest_directory = Statement(pattern=pat.dest_directory,
                           action=copy_dest_directory_handler,
                           args=None,
                           loop_continue=True,
                           continue_timer=False)

copy_statement_list = [copy_retry_message, copy_error_message, source_filename,
                       copy_file, src_file, hostname, dest_file, dest_directory,
                       host, nx_hostname, partition, config, writeto,
                       file_to_write, username, password, erase_before_copy,
                       net_type, copy_confirm, memory, copy_confirm_1,
                       copy_confirm_yes, copy_reconfirm, copy_reconfirm,
                       copy_progress, rcp_confirm, copy_overwrite, copy_nx_vrf,
                       copy_proceed, tftp_addr, copy_continue, copy_complete,
                       copy_other]


#############################################################################
# HA Reload Command  Statement
#############################################################################

pat = HaReloadPatterns()
# ha reload patterns
reload_proceed = Statement(pattern=pat.reload_proceed,
                           action=send_response,
                           args={'response': ''},
                           loop_continue=True,
                           continue_timer=True)

reload_entire_shelf = Statement(pattern=pat.reload_entire_shelf,
                                action=send_response,
                                args={'response': ''},
                                loop_continue=True,
                                continue_timer=True)

reload_this_shelf = Statement(pattern=pat.reload_this_shelf,
                              action=send_response,
                              args={'response': ''},
                              loop_continue=True,
                              continue_timer=True)

redundant = Statement(pattern=pat.redundant,
                      action=send_response,
                      args={'response': ''},
                      loop_continue=True,
                      continue_timer=True)

default_prompts = Statement(pattern=pat.default_prompts,
                            action=None,
                            args=None,
                            loop_continue=False,
                            continue_timer=False)
# TODO check this,
login_notready = Statement(pattern=pat.login_notready,
                           action=None,
                           args=None,
                           loop_continue=False,
                           continue_timer=False)

config_byte = Statement(pattern=pat.config_byte,
                        action=send_response,
                        args={'response': ''},
                        loop_continue=True,
                        continue_timer=True)

sso_ready = Statement(pattern=pat.sso_ready,
                      action=None,
                      args=None,
                      loop_continue=False,
                      continue_timer=False)

# TODO finalise on this step
loader_prompt = None
rommon_prompt = None

ha_reload_statement_list = [save_env, sso_ready, press_enter,
                            reload_proceed, reload_entire_shelf,
                            reload_this_shelf, useracess, config_byte,
                            setup_dialog, auto_install_dialog,
                            login_notready, redundant, default_prompts,
                            auto_provision, login_stmt, password_stmt,
                            generic_statements.password_ok_stmt,
                           ]

#############################################################################
# Reset Standby  Command  Statement
#############################################################################

pat = ResetStandbyPatterns()

reset_confirm = Statement(pattern=pat.reload_confirm,
                          action=send_response,
                          args={'response': ''},
                          loop_continue=True,
                          continue_timer=True)

standby_reload_confirm = Statement(pattern=pat.reload_proceed,
                                   action=None,
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=True)

reset_abort = Statement(pattern=pat.reset_abort,
                        action=reset_failure,
                        args={'error': pat.reset_abort},
                        loop_continue=False,
                        continue_timer=False)

reload_proceed1 = Statement(pattern=pat.reload_proceed1,
                            action=send_response,
                            args={'response': ''},
                            loop_continue=True,
                            continue_timer=True)

standby_reset_rp_statement_list = [save_env, reset_confirm,
                                   standby_reload_confirm, reset_abort,
                                   reload_proceed1]

#############################################################################
# Switchover Command  Statement
#############################################################################
pat = SwitchoverPatterns()


save_config = Statement(pattern=pat.save_config,
                        action=send_response, args={'response': 'no'},
                        loop_continue=True,
                        continue_timer=False)

build_config = Statement(pattern=pat.build_config,
                         action=None,
                         args=None,
                         loop_continue=True,
                         continue_timer=True)

prompt_switchover = Statement(pattern=pat.prompt_switchover,
                              action=send_response,
                              args={'response': ''},
                              loop_continue=True,
                              continue_timer=True)

switchover_init = Statement(pattern=pat.switchover_init,
                            action=None,
                            args=None,
                            loop_continue=True,
                            continue_timer=True)

switchover_reason = Statement(pattern=pat.switchover_reason,
                              action=None,
                              args=None,
                              loop_continue=True,
                              continue_timer=True)

switchover_fail1 = Statement(pattern=pat.switchover_fail1,
                             action=switchover_failure,
                             args={'error': pat.switchover_fail1},
                             loop_continue=False,
                             continue_timer=False)

switchover_fail2 = Statement(pattern=pat.switchover_fail2,
                             action=switchover_failure,
                             args={'error': pat.switchover_fail2},
                             loop_continue=False,
                             continue_timer=False)

switchover_fail3 = Statement(pattern=pat.switchover_fail3,
                             action=switchover_failure,
                             args={'error': pat.switchover_fail3},
                             loop_continue=False,
                             continue_timer=False)

switchover_fail4 = Statement(pattern=pat.switchover_fail4,
                             action=switchover_failure,
                             args={'error': pat.switchover_fail4},
                             loop_continue=False,
                             continue_timer=False)

switchover_cmd_issued = Statement(pattern=pat.switchover_cmd_issued,
                                  action=None,
                                  args=None,
                                  loop_continue=False,
                                  continue_timer=False)

switchover_statement_list = [save_config, build_config, prompt_switchover,
                             switchover_init, switchover_reason,
                             switchover_fail1, switchover_fail2,
                             switchover_fail3, switchover_fail4,
                             press_enter, login_stmt, password_stmt,
                             generic_statements.password_ok_stmt,
                             generic_statements.syslog_msg_stmt
                             ]

############################################################
# Generic Execution statement list
#############################################################

execution_statement_list = [generic_statements.confirm_prompt_y_n_stmt,
                            generic_statements.confirm_prompt_stmt,
                            generic_statements.yes_no_stmt,
                            generic_statements.syslog_msg_stmt]

configure_statement_list = [generic_statements.syslog_msg_stmt]
