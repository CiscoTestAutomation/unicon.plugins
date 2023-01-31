--------------------------------------------------------------------------------
                            New
--------------------------------------------------------------------------------
* IOSXE
    * Added Configure Error Patterns
        * "% SR feature is not configured yet, please enable Segment-routing first."
        * "% {address} overlaps with {interfaces}"
        * "%{interface} is linked to a VRF. Enable {protocol} on that VRF first."
        * "% VRF {vrf} not configured"
        * "% Incomplete command."
        * "%CLNS: System ID ({system_id}) must not change when defining additional area addresses"
        * "% Specify remote-as or peer-group commands first"
        * "% Policy commands not allowed without an address family"
        * Added switchover proceed pattern

--------------------------------------------------------------------------------
                                Fix
--------------------------------------------------------------------------------
* iosxe
    * Add support for chassis keyword argument for bash console service
    
