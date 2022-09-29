--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* generic
    * Added setting for state change prompt retries, default to 3 second wait
    * Update sudo regex pattern
    * Updated the session data to handle the reoccurring dialog issue
    * Update copy error pattern to ignore self-signed certificate failure
    * Add handlers for ping options extended_verbose, timestamp_count, record_hops, src_route_type

* iosxr/ncs5k
    * Updated the mock data for ncs5k

* iosxe
    * Added a RELOAD_WAIT to iosxe settings

* hvrp
    * Updated the pattern and setting to support configuration and error detection.


