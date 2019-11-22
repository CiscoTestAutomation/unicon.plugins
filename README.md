[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoTestAutomation/unicon.plugins)

# Unicon Plugins

Unicon is a package aiming to provide a unified connection experience to network
devices through typical command-line management interface. By wrapping the 
underlying session (eg, telnet, ssh), Unicon provides:

- direct and proxied connections through any common CLI interface (telnet, ssh, serial etc)
- power of expect-like programming without having to deal with low-level logic
- multi-vendor support through an agnostic API interface
- seamless handling of CLI modes (eg, enable, configure, admin-configure mode)
- rejected commands, command error detections
- value-add statful services (specific to the platform)

and is extensible: platform supports and services are implemented via 
open-source plugins.

Unicon is the standard, go-to CLI connection implementation for [Cisco pyATS]
framework.

[Cisco pyATS]: https://developer.cisco.com/site/pyats/

This package was initially developed internally in Cisco, and is now 
release to the general public starting late 2017 through [Cisco DevNet]. 
    
[Cisco DevNet]: https://developer.cisco.com/

# Development Mode

To start developing plugins for Unicon, clone this repository into your pyATS
virtual environment, and run `make develop`:

```shell

bash$ cd ~/pyats
bash$ git clone https://github.com/CiscoTestAutomation/unicon.plugins
bash$ cd unicon.plugins
bash$ make develop

```

# Support & Community

See https://developer.cisco.com/docs/pyats/#!license-support page for details.
