
from unicon.plugins.generic.connection_provider import GenericDualRpConnectionProvider


class AireosDualRpConnectionProvider(GenericDualRpConnectionProvider):

    def connect(self, connection_dialog=None, skip_initialization=False):
        """ Connects, initializes and designates handle

        Args:
            connection_dialog (Dialog, optional): Replacement dialog for
                initial state detection. When omitted, the normal provider
                dialog is used.
            skip_initialization (bool): Stop after initial state detection.
        """
        con = self.connection

        con.log.info('+++ connection to %s +++' % str(self.connection.a.spawn))
        con.log.info('+++ connection to %s +++' % str(self.connection.b.spawn))
        establish_kwargs = {}
        if connection_dialog is not None:
            establish_kwargs['connection_dialog'] = connection_dialog
        if skip_initialization:
            establish_kwargs['skip_initialization'] = True
        self.establish_connection(**establish_kwargs)

        # Maintain initial state
        if not con.mit and not skip_initialization:

            con.log.info('+++ designating handles +++')
            self.designate_handles()

            # Run initial exec/configure commands on the active, which is
            # supposed to disable console logging.
            con.log.info('+++ initializing active handle +++')
            self.init_active()

            # con.log.info('+++ initializing standby handle +++')
            # self.init_standby()

    def designate_handles(self):
        """ Identifies the Role of each handle and designates if it is active or
            standby and bring the active RP to enable state """
        con = self.connection

        if con.a.state_machine.current_state == 'standby':
            target_rp = 'b'
            other_rp = 'a'
        elif con.b.state_machine.current_state == 'standby':
            target_rp = 'a'
            other_rp = 'b'
        else:
            con.log.info("None of the sessions are currently in standby state")
            target_rp = 'a'
            other_rp = 'b'
        target_handle = getattr(con, target_rp)
        other_handle = getattr(con, other_rp)

        con._set_active_alias(target_rp)
        con._set_standby_alias(other_rp)

        target_handle.state_machine.go_to('enable',
                                          target_handle.spawn,
                                          context=con.context,
                                          timeout=con.connection_timeout,
                                          dialog=self.get_connection_dialog(),
                                          )
        con._handles_designated = True

    def assign_ha_mode(self):
        self.connection.a.mode = 'sso'
        self.connection.b.mode = 'sso'
