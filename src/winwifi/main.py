import io
import os
import pkgutil
import subprocess
import sys
import tempfile
import time
from typing import Callable, List, Optional
import psutil

from ctypes import *
from ctypes.wintypes import *
from comtypes import GUID

wlanapi = windll.wlanapi
openHandle = None
class WLAN_RAW_DATA(Structure):
    _fields_ = [
        ("dwDataSize", DWORD),
        ("DataBlob", c_byte * 1)
    ]


class DOT11_SSID(Structure):
    _fields_ = [("uSSIDLength", c_ulong),
                ("ucSSID", c_char * 32)]


class WLAN_INTERFACE_INFO(Structure):
    _fields_ = [
        ("InterfaceGuid", GUID),
        ("strInterfaceDescription", c_wchar * 256),
        ("isState", c_uint)
    ]


class WLAN_INTERFACE_INFO_LIST(Structure):
    _fields_ = [
        ("dwNumberOfItems", DWORD),
        ("dwIndex", DWORD),
        ("InterfaceInfo", WLAN_INTERFACE_INFO * 1)
    ]


class WindllWlanApi:
    SUCCESS = 0

    def __init__(self):
        self.native_wifi = windll.wlanapi
        self._handle = HANDLE()
        self._nego_version = DWORD()
        self._ifaces = pointer(WLAN_INTERFACE_INFO_LIST())

    def wlan_func_generator(self, func, argtypes, restypes):
        func.argtypes = argtypes
        func.restypes = restypes
        return func

    def wlan_open_handle(self, client_version=2):
        global openHandle
        f = self.wlan_func_generator(self.native_wifi.WlanOpenHandle,
                                     [DWORD, c_void_p, POINTER(DWORD), POINTER(HANDLE)],
                                     [DWORD])

        return f(client_version, None, byref(self._nego_version), byref(self._handle))
        openHandle = self._handle
    def wlan_close_handle(self):
        f = self.wlan_func_generator(self.native_wifi.WlanCloseHandle,
                                     [HANDLE, c_void_p],
                                     [DWORD])

        result = f(self._handle, None)

        print("WlanCloseHandle result:", result)  # Print the result here

        return result
    def wlan_enum_interfaces(self):
        f = self.wlan_func_generator(self.native_wifi.WlanEnumInterfaces,
                                     [HANDLE, c_void_p, POINTER(POINTER(WLAN_INTERFACE_INFO_LIST))],
                                     [DWORD])

        return f(self._handle, None, byref(self._ifaces))

    def wlan_scan(self, iface_guid):
        f = self.wlan_func_generator(self.native_wifi.WlanScan,
                                 [HANDLE, POINTER(GUID), POINTER(DOT11_SSID), POINTER(WLAN_RAW_DATA), c_void_p],
                                 [DWORD])

        return f(self._handle, iface_guid, None, None, None)

    def get_interfaes(self):
        interfaces = []
        _interfaces = cast(self._ifaces.contents.InterfaceInfo,
                           POINTER(WLAN_INTERFACE_INFO))
        for i in range(0, self._ifaces.contents.dwNumberOfItems):
            iface = {}
            iface['guid'] = _interfaces[i].InterfaceGuid
            iface['name'] = _interfaces[i].strInterfaceDescription
            interfaces.append(iface)

        return interfaces

    def is_handle_closed(self):
        return self._handle is None
class WinWiFi:
    @classmethod
    def get_profile_template(cls) -> str:
        return pkgutil.get_data(__package__, 'data/profile-template.xml').decode()

    @classmethod
    def netsh(cls, args: List[str], timeout: int = 3, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
                ['netsh'] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=timeout, check=check, encoding="cp437", shell=True)

    @classmethod
    def get_profiles(cls, callback: Callable = lambda x: None) -> List[str]:
        profiles: List[str] = []

        raw_data: str = cls.netsh(['wlan', 'show', 'profiles'], check=False).stdout.decode('cp437', errors='ignore')

        line: str
        for line in raw_data.splitlines():
            if ' : ' not in line:
                continue
            profiles.append(line.split(' : ', maxsplit=1)[1].strip())

        callback(raw_data)

        return profiles

    @classmethod
    def gen_profile(cls, ssid: str = '', auth: str = '', encrypt: str = '', passwd: str = '', remember: bool = True) \
            -> str:
        profile: str = cls.get_profile_template()

        profile = profile.replace('{ssid}', ssid)
        profile = profile.replace('{connmode}', 'auto' if remember else 'manual')

        if not passwd:
            profile = profile[:profile.index('<sharedKey>')] + \
                profile[profile.index('</sharedKey>')+len('</sharedKey>'):]
            profile = profile.replace('{auth}', 'open')
            profile = profile.replace('{encrypt}', 'none')

        return profile

    @classmethod
    def add_profile(cls, profile: str):
        fd: io.RawIOBase
        path: str
        fd, path = tempfile.mkstemp()

        os.write(fd, profile.encode())
        cls.netsh(['wlan', 'add', 'profile', 'filename={}'.format(path)])

        os.close(fd)
        os.remove(path)

    @classmethod
    def scan(cls, callback: Callable = lambda x: None) -> List['WiFiAp']:
        win_dll_wlan = WindllWlanApi()
        
        if win_dll_wlan.wlan_open_handle() is not win_dll_wlan.SUCCESS:
            raise RuntimeError('Wlan dll open handle failed !')

        process = psutil.Process(os.getpid())

        # Track the initial resource usage before starting the scan
        initial_resources = process.as_dict(attrs=['num_handles', 'memory_info'])

        try:
            if win_dll_wlan.wlan_enum_interfaces() is not win_dll_wlan.SUCCESS:
                raise RuntimeError('Wlan dll enum interfaces failed !')

            wlan_interfaces = win_dll_wlan.get_interfaes()
            if len(wlan_interfaces) == 0:
                raise RuntimeError('Do not get any wlan interfaces !')

            win_dll_wlan.wlan_scan(byref(wlan_interfaces[0]['guid']))
            time.sleep(5)

            cp: subprocess.CompletedProcess = cls.netsh(['wlan', 'show', 'networks', 'mode=bssid'])
            callback(cp.stdout)
            return list(map(WiFiAp.parse_netsh, [out for out in cp.stdout.split('\n\n') if out.startswith('SSID')]))

        finally:
            # Track the resource usage after the scan is complete
            final_resources = process.as_dict(attrs=['num_handles', 'memory_info'])

            # Calculate and print resource usage difference
            handles_diff = final_resources['num_handles'] - initial_resources['num_handles']
            memory_diff = final_resources['memory_info'].rss - initial_resources['memory_info'].rss
            close_result = win_dll_wlan.wlan_close_handle()
            if close_result != win_dll_wlan.SUCCESS:
                raise RuntimeError("uh oh")
            
            print(f"Handles used during scan: {handles_diff}")
            print(f"Memory consumed during scan (bytes): {memory_diff}")
    @classmethod
    def get_interfaces(cls) -> List['WiFiInterface']:
        cp: subprocess.CompletedProcess = cls.netsh(['wlan', 'show', 'interfaces'])
        return list(map(WiFiInterface.parse_netsh,
                        [out for out in cp.stdout.split('\n\n') if out.startswith('    Name')]))

    @classmethod
    def get_connected_interfaces(cls) -> List['WiFiInterface']:
        return list(filter(lambda i: i.state == WiFiConstant.STATE_CONNECTED, cls.get_interfaces()))

    @classmethod
    def disable_interface(cls, interface: str):
        cls.netsh(['interface', 'set', 'interface', 'name={}'.format(interface), 'admin=disabled'], timeout=15)

    @classmethod
    def enable_interface(cls, interface: str):
        cls.netsh(['interface', 'set', 'interface', 'name={}'.format(interface), 'admin=enabled'], timeout=15)

    @classmethod
    def connect(cls, ssid: str, passwd: str = '', remember: bool = True):
        if not passwd:
            for i in range(3):
                aps: List['WiFiAp'] = cls.scan()
                ap: 'WiFiAp'
                if ssid in [ap.ssid for ap in aps]:
                    break
                time.sleep(5)
            else:
                raise RuntimeError('Cannot find Wi-Fi AP')

            if ssid not in cls.get_profiles():
                ap = [ap for ap in aps if ap.ssid == ssid][0]
                cls.add_profile(cls.gen_profile(
                    ssid=ssid, auth=ap.auth, encrypt=ap.encrypt, passwd=passwd, remember=remember))
            cls.netsh(['wlan', 'connect', 'name={}'.format(ssid)])

            for i in range(30):
                if list(filter(lambda it: it.ssid == ssid, WinWiFi.get_connected_interfaces())):
                    break
                time.sleep(1)
            else:
                raise RuntimeError('Cannot connect to Wi-Fi AP')

    @classmethod
    def disconnect(cls):
        cls.netsh(['wlan', 'disconnect'])

    @classmethod
    def forget(cls, *ssids: str):
        for ssid in ssids:
            cls.netsh(['wlan', 'delete', 'profile', ssid])


class WiFiAp:
    @classmethod
    def parse_netsh(cls, raw_data: str) -> 'WiFiAp':
        ssid: str = ''
        auth: str = ''
        encrypt: str = ''
        bssid: str = ''
        strength: int = 0

        line: str
        for line in raw_data.splitlines():
            if ' : ' not in line:
                continue
            value: str = line.split(' : ', maxsplit=1)[1].strip()
            if line.startswith('SSID'):
                ssid = value
            elif line.startswith('    Authentication'):
                auth = value
            elif line.startswith('    Encryption'):
                encrypt = value
            elif line.startswith('    BSSID'):
                bssid = value.lower()
            elif line.startswith('         Signal'):
                strength = int(value[:-1])
        return cls(ssid=ssid, auth=auth, encrypt=encrypt, bssid=bssid, strength=strength, raw_data=raw_data)

    def __init__(
            self,
            ssid: str = '',
            auth: str = '',
            encrypt: str = '',
            bssid: str = '',
            strength: int = 0,
            raw_data: str = '',
    ):
        self._ssid: str = ssid
        self._auth: str = auth
        self._encrypt: str = encrypt
        self._bssid: str = bssid
        self._strength: int = strength
        self._raw_data: str = raw_data

    @property
    def ssid(self) -> str:
        return self._ssid

    @property
    def auth(self) -> str:
        return self._auth

    @property
    def encrypt(self) -> str:
        return self._encrypt

    @property
    def bssid(self) -> str:
        return self._bssid

    @property
    def strength(self) -> int:
        return self._strength

    @property
    def raw_data(self) -> str:
        return self._raw_data


class WiFiConstant:
    STATE_CONNECTED = 'connected'
    STATE_DISCONNECTED = 'disconnected'


class WiFiInterface:
    @classmethod
    def parse_netsh(cls, raw_data: str) -> 'WiFiInterface':
        name: str = ''
        state: str = ''
        ssid: str = ''
        bssid: str = ''

        line: str
        for line in raw_data.splitlines():
            if ' : ' not in line:
                continue
            value: str = line.split(' : ', maxsplit=1)[1].strip()
            if line.startswith('    Name'):
                name = value
            elif line.startswith('    State'):
                state = value
            elif line.startswith('    SSID'):
                ssid = value
            elif line.startswith('    BSSID'):
                bssid = value

        c: 'WiFiInterface' = cls(name=name, state=state)
        if ssid:
            c.ssid = ssid
        if bssid:
            c.bssid = bssid
        return c

    def __init__(
            self,
            name: str = '',
            state: str = '',
            ssid: Optional[str] = None,
            bssid: Optional[str] = None,
    ):
        self._name: str = name
        self._state: str = state
        self._ssid: Optional[str] = ssid
        self._bssid: Optional[str] = bssid

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> str:
        return self._state

    @property
    def ssid(self) -> Optional[str]:
        return self._ssid

    @ssid.setter
    def ssid(self, value: str):
        self._ssid = value

    @property
    def bssid(self) -> Optional[str]:
        return self._bssid

    @bssid.setter
    def bssid(self, value: str):
        self._bssid = value
