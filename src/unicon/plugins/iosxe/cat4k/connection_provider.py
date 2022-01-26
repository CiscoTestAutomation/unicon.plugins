"""
Authors:
       Omid Mehrabian: omehrabi@cisco.com
"""


from unicon.bases.routers.connection_provider import BaseDualRpConnectionProvider
from unicon.plugins.generic.statements import connection_statement_list
from concurrent.futures import ThreadPoolExecutor, wait as wait_futures, FIRST_COMPLETED
from unicon.eal.dialogs import Dialog

class Cat4kDualRpConnectionProvider(BaseDualRpConnectionProvider):
    """ Implements Stack Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to stack device
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the base connection provider
        """
        super().__init__(*args, **kwargs)

    def unlock_standby(self, *args, **kwargs):
        pass
    def init_standby(self, *args, **kwargs):
        pass

    def designate_handles(self, *args, **kwargs):
        """ Identifies the Role of each handle and designates if it is active or
            standby and bring the active RP to enable state """

        con=self.connection
        con.log.info('+++ designating handles +++')
        subcons = list(con._subconnections.items())
        subcon1_alias, subcon1 = subcons[0]
        subcon2_alias, subcon2 = subcons[1]

        # Try to go to enable mode on both connections
        for subcon in [subcon1, subcon2]:
            try:
                subcon.state_machine.go_to(
                    'enable',
                    subcon.spawn,
                    context=subcon.context,
                )
            except Exception:
                pass
            con.log.debug('{} in state: {}'.format(subcon.alias, subcon.state_machine.current_state))

        if subcon1.state_machine.current_state == 'enable':
            target_alias = subcon1_alias
            other_alias = subcon2_alias
        elif subcon2.state_machine.current_state == 'enable':
            target_alias = subcon2_alias
            other_alias = subcon1_alias

        con._set_active_alias(target_alias)
        con._set_standby_alias(other_alias)
        con._handles_designated = True

    def establish_connection(self):

        """ Reads the device state and brings both RP to the right state
        """
        con = self.connection
        subconnections = con.subconnections

        for subconnection in subconnections:
            learn_hostname = subconnection.learn_hostname and not \
                subconnection.learned_hostname
            if learn_hostname:
                subconnection.state_machine.learn_hostname = True
            subconnection.state_machine.learn_pattern = \
                con.settings.DEFAULT_LEARNED_HOSTNAME

        for subconnection in subconnections:
            context = subconnection.context
            context.update(cred_list=context.get('login_creds'))
        futures = []


        def detect_state(subcon, dialog= None):
            subcon.sendline()
            try:
                subcon.state_machine.go_to(
                    'any',
                    subcon.spawn,
                    context=subcon.context,
                    prompt_recovery=subcon.prompt_recovery,
                    timeout=subcon.connection_timeout,
                    dialog=Dialog(connection_statement_list)
                )
            except Exception as e:
                subcon.log.info(e)
            subcon.log.debug('{} in state: {}'.format(subcon.alias, subcon.state_machine.current_state))

        executer= ThreadPoolExecutor(max_workers = len(subconnections))
        for subcon in subconnections:
            futures.append(executer.submit(
                # Check current state
                detect_state,
                subcon=subcon,
                dialog=self.get_connection_dialog()))
        wait_futures(futures, timeout=3, return_when=FIRST_COMPLETED)

        for subconnection in subconnections:
            context = subconnection.context
            context.pop('cred_list', None)

        if learn_hostname:
            # Use the learned hostname in %N substitutions from this point on.
            learned_hostname = con.settings.DEFAULT_LEARNED_HOSTNAME
            for subconnection in subconnections:
                subcon_learned_hostname = subconnection._get_learned_hostname(
                    spawn=subconnection.spawn)
                if subcon_learned_hostname != \
                        con.settings.DEFAULT_LEARNED_HOSTNAME:
                    learned_hostname = subcon_learned_hostname
                    break
            if learned_hostname == con.settings.DEFAULT_LEARNED_HOSTNAME:
                con.log.warning(
                    'Failed to learn the hostname.  '
                    'Using the default hostname pattern {}. '
                    'This may lead to unstable behavior.'.\
                    format(self.connection.settings.DEFAULT_LEARNED_HOSTNAME))

            con.learned_hostname = learned_hostname
            for subconnection in subconnections:
                subconnection.learned_hostname = learned_hostname
                subconnection.state_machine.learn_hostname = False

