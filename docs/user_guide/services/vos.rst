VOS
===

This section lists the CLI services which are supported with the Voice Operating System plugin.

  * `execute <#execute>`__

The following generic services are also available:

  * `send`_
  * `sendline`_
  * `expect`_

.. _send: generic_services.html#send
.. _sendline: generic_services.html#sendline
.. _expect: generic_services.html#expect



execute
-------

This service is used to execute arbitrary commands on the device. Though it is
intended to execute non-interactive commands. In case you want to execute
an command that uses interactive responses use `reply` option to specify 
the Dialog object that handles the responses.

===============   ======================    =====================================================
Argument          Type                      Description
===============   ======================    =====================================================
command           str                       command to execute
timeout           int (default 60 sec)      (optional) timeout value for the overall interaction.
reply             Dialog                    (optional)  additional dialog
lines             int (default 100)         (optional)  number of lines to capture when paging
===============   ======================    =====================================================

The `execute` service returns the output of the command in string format
or it raises an exception. You can expect a SubCommandFailure
error in case anything goes wrong.

The execute service will response to the following prompts automatically:

  * Press <enter> for 1 line, <space> for one page, or <q> to quit
  * options: q=quit, n=next, p=prev, b=begin, e=end (lines 61 - 80 of 207554) :

The response to the first prompt will be to send a space. For the second prompt, 
paging will be done by sending `n` automatically for up to 100 lines by default.
If you want to capture more lines, specify the `lines` option.

The paging prompts will be stripped from the output.


.. code-block:: python

        #Example
        --------

        from unicon import Connection

        ucm = Connection(hostname='ucm',
                         start=['ssh 10.0.0.1'],
                         os='vos',
                         credentials={'default': {'username': 'admin', 'password': 'cisco123'}})

        ucm.connect()

        # single command
        output = ucm.execute("show hardware")

        # command with paging using non-default number of lines
        output = ucm.execute("file view activelog /path/to/logfile.txt", lines=250)



Example with paging prompts stripped from output.


.. code-block:: python

        >>> output = ucm.execute('show hardware')

        2017-10-26T20:01:04: %UNICON-INFO: +++ execute  +++
        show hardware

        HW Platform       : VMware Virtual Machine
        Processors        : 2
        Press <enter> for 1 line, <space> for one page, or <q> to quitType              : Intel(R) Xeon(R) CPU           E5640  @ 2.67GHz
        CPU Speed         : 2670
        Press <enter> for 1 line, <space> for one page, or <q> to quitMemory            : 6144 MBytes
        Object ID         : 1.3.6.1.4.1.9.1.1348
        Press <enter> for 1 line, <space> for one page, or <q> to quitOS Version        : UCOS 6.0.0.0-2.i386
        Serial Number     : VMware-00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 01
        Press <enter> for 1 line, <space> for one page, or <q> to quit
        RAID Version      :
        No RAID controller information is available
        Press <enter> for 1 line, <space> for one page, or <q> to quit
        BIOS Information  :
        PhoenixTechnologiesLTD 6.00 09/21/2015
        Press <enter> for 1 line, <space> for one page, or <q> to quit
        RAID Details      :
        No RAID information is available
        Press <enter> for 1 line, <space> for one page, or <q> to quit-----------------------------------------------------------------------
        Physical device information
        Press <enter> for 1 line, <space> for one page, or <q> to quit-----------------------------------------------------------------------
        Number of Disks   : 1
        Press <enter> for 1 line, <space> for one page, or <q> to quitHard Disk #1
        Size (in GB)      : 80
        Press <enter> for 1 line, <space> for one page, or <q> to quit
        Partition Details :

        Press <enter> for 1 line, <space> for one page, or <q> to quitDisk /dev/sda: 10443 cylinders, 255 heads, 63 sectors/track
        Units = sectors of 512 bytes, counting from 0
        Press <enter> for 1 line, <space> for one page, or <q> to quit
           Device Boot    Start       End   #sectors  Id  System
        /dev/sda1   *      2048  29028351   29026304  83  Linux
        Press <enter> for 1 line, <space> for one page, or <q> to quit/dev/sda2      29028352  58054655   29026304  83  Linux
        /dev/sda3      58054656  58578943     524288  83  Linux
        Press <enter> for 1 line, <space> for one page, or <q> to quit/dev/sda4      58578944 167772159  109193216   5  Extended
        /dev/sda5      58580992  66772991    8192000  82  Linux swap / Solaris
        Press <enter> for 1 line, <space> for one page, or <q> to quit/dev/sda6      66775040 167772159  100997120  83  Linux
        admin:>>> 
        >>> 
        >>> print(output)
        HW Platform       : VMware Virtual Machine
        Processors        : 2
        Type              : Intel(R) Xeon(R) CPU           E5640  @ 2.67GHz
        CPU Speed         : 2670
        Memory            : 6144 MBytes
        Object ID         : 1.3.6.1.4.1.9.1.1348
        OS Version        : UCOS 6.0.0.0-2.i386
        Serial Number     : VMware-00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 01

        RAID Version      :
        No RAID controller information is available

        BIOS Information  :
        PhoenixTechnologiesLTD 6.00 09/21/2015

        RAID Details      :
        No RAID information is available
        -----------------------------------------------------------------------
        Physical device information
        -----------------------------------------------------------------------
        Number of Disks   : 1
        Hard Disk #1
        Size (in GB)      : 80

        Partition Details :

        Disk /dev/sda: 10443 cylinders, 255 heads, 63 sectors/track
        Units = sectors of 512 bytes, counting from 0

           Device Boot    Start       End   #sectors  Id  System
        /dev/sda1   *      2048  29028351   29026304  83  Linux
        /dev/sda2      29028352  58054655   29026304  83  Linux
        /dev/sda3      58054656  58578943     524288  83  Linux
        /dev/sda4      58578944 167772159  109193216   5  Extended
        /dev/sda5      58580992  66772991    8192000  82  Linux swap / Solaris
        /dev/sda6      66775040 167772159  100997120  83  Linux
        >>> 


Example with paging up to 50 lines.

.. code-block:: python

        >>> r = c.execute('file view activelog /cm/trace/dbl/showtechdbstateinfo211506.txt', lines=50)

        2017-10-26T22:18:32: %UNICON-INFO: +++ execute  +++
        file view activelog /cm/trace/dbl/showtechdbstateinfo211506.txt



        ====================
        Executing onstat  -V 
        ====================
        IBM Informix Dynamic Server Version 12.10.UC7X3 Software Serial Number AAA#B000000


        ====================
        Executing onstat  -m 
        ====================

        IBM Informix Dynamic Server Version 12.10.UC7X3 -- On-Line -- Up 3 days 06:07:15 -- 286648 Kbytes

        Message Log File: /var/log/active/cm/log/informix/ccm.log
        20:58:38  Checkpoint Statistics - Avg. Txn Block Time 0.000, # Txns blocked 0, Plog used 22, Llog used 25

        21:03:38  Checkpoint Completed:  duration was 0 seconds.
        21:03:38  Thu Oct 12 - loguniq 41, logpos 0x1075f018, timestamp: 0xd0a64de Interval: 14051


        options: q=quit, n=next, p=prev, b=begin, e=end (lines 1 - 20 of 189216) : 
        21:03:38  Maximum server connections 76 
        21:03:38  Checkpoint Statistics - Avg. Txn Block Time 0.000, # Txns blocked 0, Plog used 29, Llog used 40

        21:08:38  Checkpoint Completed:  duration was 0 seconds.
        21:08:38  Thu Oct 12 - loguniq 41, logpos 0x10771018, timestamp: 0xd0a7468 Interval: 14052

        21:08:38  Maximum server connections 76 
        21:08:38  Checkpoint Statistics - Avg. Txn Block Time 0.000, # Txns blocked 0, Plog used 19, Llog used 18

        21:13:40  Checkpoint Completed:  duration was 1 seconds.
        21:13:40  Thu Oct 12 - loguniq 41, logpos 0x107b7018, timestamp: 0xd0a885d Interval: 14053

        21:13:40  Maximum server connections 76 
        21:13:40  Checkpoint Statistics - Avg. Txn Block Time 0.000, # Txns blocked 0, Plog used 77, Llog used 70




        ====================
        Executing onstat  -c 

        options: q=quit, n=next, p=prev, b=begin, e=end (lines 21 - 40 of 189216) : 
        ====================

        IBM Informix Dynamic Server Version 12.10.UC7X3 -- On-Line -- Up 3 days 06:07:15 -- 286648 Kbytes

        Configuration File: /usr/local/cm/db/informix/etc/onconfig



        ====================
        Executing onstat  -b 
        ====================

        IBM Informix Dynamic Server Version 12.10.UC7X3 -- On-Line -- Up 3 days 06:07:15 -- 286648 Kbytes

        Buffers
        address  userthread flgs pagenum          memaddr  nslots pgflgs xflgs owner    waitlist

        Buffer pool page size: 2048
         97 modified, 40000 total, 65536 hash buckets, 2048 buffer size


        options: q=quit, n=next, p=prev, b=begin, e=end (lines 41 - 60 of 189216) : 
        admin:>>> 
        >>> print(r)
        ====================
        Executing onstat  -V 
        ====================
        IBM Informix Dynamic Server Version 12.10.UC7X3 Software Serial Number AAA#B000000


        ====================
        Executing onstat  -m 
        ====================

        IBM Informix Dynamic Server Version 12.10.UC7X3 -- On-Line -- Up 3 days 06:07:15 -- 286648 Kbytes

        Message Log File: /var/log/active/cm/log/informix/ccm.log
        20:58:38  Checkpoint Statistics - Avg. Txn Block Time 0.000, # Txns blocked 0, Plog used 22, Llog used 25

        21:03:38  Checkpoint Completed:  duration was 0 seconds.
        21:03:38  Thu Oct 12 - loguniq 41, logpos 0x1075f018, timestamp: 0xd0a64de Interval: 14051

        21:03:38  Maximum server connections 76 
        21:03:38  Checkpoint Statistics - Avg. Txn Block Time 0.000, # Txns blocked 0, Plog used 29, Llog used 40

        21:08:38  Checkpoint Completed:  duration was 0 seconds.
        21:08:38  Thu Oct 12 - loguniq 41, logpos 0x10771018, timestamp: 0xd0a7468 Interval: 14052

        21:08:38  Maximum server connections 76 
        21:08:38  Checkpoint Statistics - Avg. Txn Block Time 0.000, # Txns blocked 0, Plog used 19, Llog used 18

        21:13:40  Checkpoint Completed:  duration was 1 seconds.
        21:13:40  Thu Oct 12 - loguniq 41, logpos 0x107b7018, timestamp: 0xd0a885d Interval: 14053

        21:13:40  Maximum server connections 76 
        21:13:40  Checkpoint Statistics - Avg. Txn Block Time 0.000, # Txns blocked 0, Plog used 77, Llog used 70




        ====================
        Executing onstat  -c 
        ====================

        IBM Informix Dynamic Server Version 12.10.UC7X3 -- On-Line -- Up 3 days 06:07:15 -- 286648 Kbytes

        Configuration File: /usr/local/cm/db/informix/etc/onconfig



        ====================
        Executing onstat  -b 
        ====================

        IBM Informix Dynamic Server Version 12.10.UC7X3 -- On-Line -- Up 3 days 06:07:15 -- 286648 Kbytes

        Buffers
        address  userthread flgs pagenum          memaddr  nslots pgflgs xflgs owner    waitlist

        Buffer pool page size: 2048
         97 modified, 40000 total, 65536 hash buckets, 2048 buffer size

        >>> 



.. sectionauthor:: Dave Wapstra <dwapstra@cisco.com>


