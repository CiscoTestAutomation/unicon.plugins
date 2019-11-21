
# Q&D Helper script to generate the ReStructered text file for the dialogs
# prints to stdout

import os, sys
import unicon
import traceback
from unicon import Connection
from unicon.eal.dialogs import Dialog

from ats.datastructures import AttrDict


def find_plugins():
    plugin_path = os.path.dirname(unicon.plugins.__file__)
    plugin_list = []
    for subdir, dirs, files in os.walk(plugin_path):
        for file in files:
            if file == '__init__.py':
                with open(os.path.join(subdir, file), 'rb') as f:
                    content_length = len(f.read().strip())
                if content_length:
                    plugin = os.path.relpath(subdir, start=plugin_path)
                    p = plugin.split('/')
                    plugin_attributes = AttrDict()
                    if len(p):
                        plugin_attributes.os = p[0]
                    if len(p) > 1:
                        plugin_attributes.series = p[1]
                    else:
                        plugin_attributes.series = None
                    if len(p) > 2:
                        plugin_attributes.model = p[2]
                    else:
                        plugin_attributes.model = None
                    plugin_list.append(plugin_attributes)
    return plugin_list


def print_dialogs(service, dialogs):

    if not len(list(dialogs)):
        return

    print('\n\n%s' % service)
    print('~' * len(service) + '\n')

    dialog_list = []
    dialog_pattern_list = []

    for d in dialogs:
        if d.pattern in dialog_pattern_list:
            print('.. warning:: Duplicate statement {}'.format(d))
        dialog_pattern_list.append(d.pattern)
        if hasattr(d, 'action') and d.action and d.action.__name__ != 'exec_state_change_action':
            if d.action.__name__ not in [d.__name__ for d in dialog_action_list]:
                dialog_action_list.append(d.action)
            dialog_list.append([d.pattern.replace('\r', '\\r').replace('\n', '\\n'),
                                "{}({})".format(d.action.__name__, d.args if d.args else '')])

    print("""
.. table::
   :widths: auto
   :align: left
""")

    len1 = 0
    len2 = 0
    for l in dialog_list:
        if len(l[0]) > len1:
            len1 = len(l[0])
        if len(l[1]) > len2:
            len2 = len(l[1])

    print('\n   ' + '=' * (len1 + 4) + ' ' + '=' * (len2))
    s = "   {}%s {:<%s}" % (' ' * (len1 - len('Pattern') + 4), len2)
    print(s.format('Pattern', 'Action'))
    print('   ' + '-' * (len1 + 4) + ' ' + '-' * (len2))

    for l in dialog_list:
        s = "   ``{}``%s {:<%s}" % (' ' * (len1 - len(l[0])), len2)
        print(s.format(l[0], l[1]))

    print('   ' + '=' * (len1 + 4) + ' ' + '=' * (len2))


if __name__ == "__main__":

    print("""

Service Patterns
================

.. note::

    This document is automatically generated and is intended to document
    the default per-platform patterns used to match CLI dialogs for each 
    plugin, and the corresponding action when a pattern is matched.

""")

    def plugin_os(p):
        if p.series:
            return '%s%s' % (p.os, p.series)
        else:
            return p.os

    dialog_action_list = []

    plugins = find_plugins()
    for p in sorted(plugins, key=plugin_os):

        plugin_name = p.os
        _os = p.os
        if p.series:
            plugin_name += "/%s" % p.series
            series = p.series
        else:
            series = None
        
        try:
            c = Connection(hostname='Router', start=['bash'], os=_os, series=series, log_stdout=False)
            # c = Connection(hostname='Router', start=['bash'], os=_os, series=series)
            c.init_service()
            c.connection_provider = c.connection_provider_class(c)
        
        except:
            print('---------------- ERROR ---------------', file = sys.stderr)
            traceback.print_exc()
            print('--------------------------------------', file = sys.stderr)

        else:
            print('\n\n')
            print(plugin_name)
            print('-' * len(plugin_name) + '\n')

            print_dialogs('default', c.state_machine.default_dialog)

            print_dialogs('connect', c.connection_provider.get_connection_dialog())

            print_dialogs('execute', c.execute.dialog if c.execute.dialog else Dialog([]))
