
from unicon.plugins.generic.connection_provider import GenericDualRpConnectionProvider


class AireosDualRpConnectionProvider(GenericDualRpConnectionProvider):


    def connect(self):
        """ Connects, initializes and designates handle
        """
        con = self.connection

        con.log.info('+++ connection to %s +++' % str(self.connection.a.spawn))
        con.log.info('+++ connection to %s +++' % str(self.connection.b.spawn))
        self.establish_connection()

        # Maintain initial state
        if not con.mit:

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
