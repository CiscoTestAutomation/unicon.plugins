September 2020
==============

September 29th
--------------

.. csv-table:: Module Versions
    :header: "Modules", "Versions"

        ``unicon``, v20.9


Install Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install unicon


Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bash$ pip install --upgrade unicon


Features and Bug Fixes:
^^^^^^^^^^^^^^^^^^^^^^^

* Fixed learn_hostname for ha standby device
* Updated dialog processor default timeout to use spawn timeout instead
* Updated general connect function to use self.connected to check connectivity
* Updated dual_rp connection when chassis type is specified, subconnection use single_rp chassis type
