Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^
- Added error patterns corresponding to device.configure() service under NXOS.

- separate plugins from unicon

- add prompt matched_retries for execute service to avoid transient match on output

- enhance linux plugin to set TERM vt100 and LC_ALL C by default

- add plugins sdwan/viptela and sdwan/iosxe

- enhance iosxe/cat3k to find boot image from rommon

- aireos plugin updates: support known states, support for hostname learning
  `execute` service raises SubCommandFailure if error is detected in CLI output.

- Regex added for Resolve AS number option

- IOSXE and Generic plugins were modified. Service pattern added to support "Resolve AS number" output. VRF variable support added for IOSXE Traceroute
