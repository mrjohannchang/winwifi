import pkg_resources
import plumbum.cli
import sys
from typing import Tuple

from .main import WinWifi


class Wifi(plumbum.cli.Application):
    PROGNAME: str = 'wifi'
    VERSION: str = pkg_resources.require('winwifi')[0].version
    DESCRIPTION: str = 'A Windows Wi-Fi CLI'


@Wifi.subcommand('scan')
class WifiScan(plumbum.cli.Application):
    _refresh: bool = False

    @plumbum.cli.switch(['--refresh'], help='Force to refresh the Wi-Fi AP list')
    def refresh(self):
        self._refresh = True

    def main(self):
        WinWifi.scan(refresh=self._refresh, callback=lambda x: print(x))


@Wifi.subcommand('connect')
class WifiConnect(plumbum.cli.Application):
    _one_shot: bool = False

    @plumbum.cli.switch(['--oneshot'], help='Do not remember the connection')
    def one_shot(self):
        self._one_shot = True

    def main(self, ssid: str, passwd: str = ''):
        WinWifi.connect(ssid=ssid, passwd=passwd, remember=not self._one_shot)


@Wifi.subcommand('disconnect')
class WifiDisconnect(plumbum.cli.Application):
    def main(self):
        WinWifi.disconnect()


@Wifi.subcommand('history')
class WifiHistory(plumbum.cli.Application):
    def main(self):
        WinWifi.get_profiles(callback=lambda x: print(x))


@Wifi.subcommand('forget')
class WifiForget(plumbum.cli.Application):
    def main(self, *ssids: str):
        WinWifi.forget(*ssids)


def main() -> int:
    return Wifi.run()


if __name__ == '__main__':
    sys.exit(main())
