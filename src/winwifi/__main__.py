import os
import pkg_resources
import plumbum.cli
import sys
from typing import List

from .main import WiFiConstant, WiFiInterface, WinWiFi


class Wifi(plumbum.cli.Application):
    """A Windows Wi-Fi CLI"""

    PROGNAME: str = 'wifi'
    VERSION: str = pkg_resources.require('winwifi')[0].version


@Wifi.subcommand('scan')
class WifiScan(plumbum.cli.Application):
    """Scan and list nearby Wi-Fi access points"""

    _refresh: bool = False

    @plumbum.cli.switch(['--refresh'], help='Force to refresh the Wi-Fi AP list')
    def refresh(self):
        self._refresh = True

    def main(self):
        WinWiFi.scan(refresh=self._refresh, callback=lambda x: print(x))


@Wifi.subcommand('connect')
class WifiConnect(plumbum.cli.Application):
    """Connect to a specific access point"""

    _one_shot: bool = False

    @plumbum.cli.switch(['--oneshot'], help='Do not remember the connection')
    def one_shot(self):
        self._one_shot = True

    def main(self, ssid: str, passwd: str = ''):
        WinWiFi.connect(ssid=ssid, passwd=passwd, remember=not self._one_shot)


@Wifi.subcommand('connected')
class WifiConnected(plumbum.cli.Application):
    """Show the current connected Wi-Fi SSID"""

    def main(self):
        interface: WiFiInterface
        interfaces: List[WiFiInterface] = [interface.ssid for interface in WinWiFi.get_interfaces()
                                           if interface.state == WiFiConstant.STATE_CONNECTED]
        if not interfaces:
            return 1
        print(os.linesep.join(interfaces))


@Wifi.subcommand('disconnect')
class WifiDisconnect(plumbum.cli.Application):
    """Disconnect from a Wi-Fi access point"""

    def main(self):
        WinWiFi.disconnect()


@Wifi.subcommand('history')
class WifiHistory(plumbum.cli.Application):
    """List the historical Wi-Fi access points"""

    def main(self):
        WinWiFi.get_profiles(callback=lambda x: print(x))


@Wifi.subcommand('forget')
class WifiForget(plumbum.cli.Application):
    """Remove speicifc access points from the historical list"""

    def main(self, *ssids: str):
        WinWiFi.forget(*ssids)


def main() -> int:
    return Wifi.run()[1]


if __name__ == '__main__':
    sys.exit(main())
