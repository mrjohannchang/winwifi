winwifi
=======

A Wi-Fi CLI for Windows.

Installation
------------

.. code:: sh

    pip install winwifi

Usage
-----

::

    wifi 0.0.4

    A Windows Wi-Fi CLI

    Usage:
        wifi [SWITCHES] [SUBCOMMAND [SWITCHES]] args...

    Meta-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits

    Subcommands:
        connect            Connect to a specific access point; see 'wifi connect --help' for more info
        disconnect         Disconnect from a Wi-Fi access point; see 'wifi disconnect --help' for more info
        forget             Remove speicifc access points from the historical list; see 'wifi forget --help' for more info
        history            List the historical Wi-Fi access points; see 'wifi history --help' for more info
        scan               Scan and list nearby Wi-Fi access points; see 'wifi scan --help' for more info

    wifi connect 0.0.4

    Connect to a specific access point

    Usage:
        wifi connect [SWITCHES] ssid [passwd='']

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits

    Switches
        --oneshot          Do not remember the connection


    wifi disconnect 0.0.4

    Disconnect from a Wi-Fi access point

    Usage:
        wifi disconnect [SWITCHES]

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits


    wifi forget 0.0.4

    Remove speicifc access points from the historical list

    Usage:
        wifi forget [SWITCHES] ssids...

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits


    wifi history 0.0.4

    List the historical Wi-Fi access points

    Usage:
        wifi history [SWITCHES]

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits


    wifi scan 0.0.4

    Scan and list nearby Wi-Fi access points

    Usage:
        wifi scan [SWITCHES]

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits

    Switches
        --refresh          Force to refresh the Wi-Fi AP list
