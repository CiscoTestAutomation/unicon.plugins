Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

- iosxe plugin

    - Now copy service passes in vrf via the command line instead of
      expecting to be prompted for vrf.

- generic and iosxe/cat3k plugins

    - Fixed reload service timeout issue, now waiting longer when
      connecting after reload.
