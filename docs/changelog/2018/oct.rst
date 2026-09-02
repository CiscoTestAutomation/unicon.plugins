October 2018
============

Oct 9 - v3.4.0
---------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

    ``unicon``, v3.4.0


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon

Features and Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^

- fixed unicon logging with pyATS where forkeds/pcalls were not being
  respected

- added new feature where now each device gets its own overall send/receive
  log

- significantly optimized unicon log handling in general

- optimized log output to be more human friendly, indicating which device
  it's coming from

- removed blinker package dependency

- modified yaml.load to yaml.safe_load for CVE-2017-18342

- Linux prompt pattern updated for ESA WSA and SMA appliances

- Update Confd/NFVIS plugin to allow default hostname of nfvis
