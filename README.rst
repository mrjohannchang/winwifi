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

    wifi 0.0.1

    A Windows Wi-Fi CLI

    Usage:
        wifi [SWITCHES] [SUBCOMMAND [SWITCHES]] args...

    Meta-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits

    Subcommands:
        connect            see 'wifi connect --help' for more info
        disconnect         see 'wifi disconnect --help' for more info
        forget             see 'wifi forget --help' for more info
        history            see 'wifi history --help' for more info
        scan               see 'wifi scan --help' for more info

    wifi connect 0.0.1

    Usage:
        wifi connect [SWITCHES] ssid [passwd='']

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits

    Switches
        --oneshot          Do not remember the connection


    wifi disconnect 0.0.1

    Usage:
        wifi disconnect [SWITCHES]

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits


    wifi forget 0.0.1

    Usage:
        wifi forget [SWITCHES] ssids...

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits


    wifi history 0.0.1

    Usage:
        wifi history [SWITCHES]

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits


    wifi scan 0.0.1

    Usage:
        wifi scan [SWITCHES]

    Hidden-switches
        -h, --help         Prints this help message and quits
        --help-all         Print help messages of all subcommands and quit
        -v, --version      Prints the program's version and quits

    Switches
        --refresh          Force to refresh the Wi-Fi AP list
