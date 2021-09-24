Playback
========

Demos and devices, don't mix together. In the middle of a demo, the
device will react differently than expected just for the sake of it.

`Unicon.playback` records all interaction with any device and can be
replayed later at any time. With this recording it is then possible to create a
:ref:`mock device<mock>`. A mock device is awesome! It gives you a python
device which can be connected to, and output show commands. Perfect for demo.

Here are a few possible scenario with record/playback:

* Create examples/demo/training with recorded device interaction, no need to have a device available! 
* Reproduce parser, library, script issues without having the device available!
* Devices are not always available, record it once and it can be used forever!

`Unicon.playback` is the perfect tool for training, reproduce complicated
issues in scripts and even just to manage your device availability.

This is perfect when sending a bug report for certain tools where the device
interaction is needed. Record the session, and send the recorded directory.

Replay can manipulate time, allowing re-run script much faster than it was
recorded.

Here is a recording of it in action.

.. raw:: html

    <script id="asciicast-0aEM9Oi07kPIn6tdKGmPLxTBm" src="https://asciinema.org/a/0aEM9Oi07kPIn6tdKGmPLxTBm.js" async></script>

Record
------

At the end of your command line, add the record arguments. There is a single
argument which accepts a directory to store the recording. The recording
generates a pickle_ file per device. If the directory does not exist, it will
create it automatically.

.. csv-table:: Record argument
    :header: Argument, Description
    :widths: 30, 70

    ``--record``, "Directory where to store the recording"

Here are a few examples on how to use it.

.. code-block:: bash

    easypy jobfile.py -testbed_file mytestbed.yaml --record recording1
    python script.py -testbed_file mytestbed.yaml --record recording1

In case the dash argument cannot be used, environment variable
``UNICON_RECORD`` can be used instead.

.. code-block:: bash

    export UNICON_RECORD=recording1
 
.. note::

    There is currently a limitation with Pcall, only one device connection can
    be recorded.

Replay
------

Now you can use the recorded information instead of reserving the device. To
replay, add the replay argument. This will not connect to the devices but
instead use the recorded session.

.. csv-table:: Replay argument
    :header: Argument, Description
    :widths: 30, 70

    ``--replay``, "Directory where the stored recording is held"
    ``--speed``, "Modify the speed of device interaction"

Here a few examples on how to use it.

.. code-block:: bash

    easypy jobfile.py -testbed_file mytestbed.yaml --replay recording1
    python script.py -testbed_file mytestbed.yaml --replay recording1

    # Let's make it 4 times faster
    easypy jobfile.py -testbed_file mytestbed.yaml --replay recording1 --speed 4

    # Let's make it 4 times slower
    easypy jobfile.py -testbed_file mytestbed.yaml --replay recording1 --speed .25

In case the dash argument cannot be used, environment variable
``UNICON_REPLAY`` and ``UNICON_REPLAY_SPEED`` can be used instead.

.. code-block:: bash

    export UNICON_REPLAY=recording1
    export UNICON_REPLAY_SPEED=4

Mock Device
-----------

Unicon provides the functionality to create a :ref:`mock device <mock>`. This
is driven by a yaml which can either be created manually or created dynamically
from a recording.

.. code-block:: bash

    python -m unicon.playback.mock --recorded-data recorded/nx-osv-1 --output data/nxos/mock_data.yaml

This file can then be used to create a mock device.

.. code-block:: bash

    python -m unicon.mock.mock_device --os nxos --mock_data_dir data --state connect

This provides a device which can be interacted and used in testscript.

.. code-block:: bash

        connections:
          defaults:
            class: 'unicon.Unicon'
          a:
            command: mock_device_cli --os iosxe --mock_data_dir data --state connect
            protocol: unknown

Here is a recording on creating a mock with a big amount of show commands.

.. raw:: html

    <script id="asciicast-WU9egjeFtJQiW8vIlD0SH9HvV" src="https://asciinema.org/a/WU9egjeFtJQiW8vIlD0SH9HvV.js" async></script>

.. _pickle: https://docs.python.org/3/library/pickle.html

By default, when a mock device is created, it will only store the first output of each command in the YAML file, regardless of the number of times the command was executed.
If you wish to record all the commands and to be able to execute them multiple times, you can do so by passing the argument ``--allow-repeated-commands``.

.. code-block:: bash

    python -m unicon.playback.mock --recorded-data recorded/nx-osv-1 --output data/nxos/mock_data.yaml --allow-repeated-commands

If you take a look at the resulting YAML file, you will notice that each stored command will have a structure similar to the one below:

.. code-block:: yaml

        execute:
          commands:
            show interfaces GigabitEthernet1:
              response:
                - "GigabitEthernet1 is up, line protocol is up..."
                - "GigabitEthernet1 is up, line protocol is up..."
              response_type: circular

With this yaml file you will never run out of outputs for this command as it will circle between the outputs every time the command is called.