import threading

import dbus
import dbus.mainloop.glib
from gi.repository import GLib

from heraldo.beacons.base import Beacon
from heraldo.exceptions import AdvertisementError, BlueZNotAvailableError
from heraldo.bluez.advertisement import Advertisement

_BLUEZ_SERVICE = "org.bluez"
_LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
_DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
_DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"

_REPLY_TIMEOUT = 5.0  # seconds to wait for BlueZ acknowledgement


class Advertiser:
    """
    Registers BLE beacon advertisements with BlueZ via DBus.

    Maintains a GLib mainloop on a daemon thread so that BlueZ can call back
    into our Advertisement objects. Supports use as a context manager.

    Usage::

        with Advertiser() as advertiser:
            ad = advertiser.register(IBeacon(uuid="...", major=1, minor=1))
            time.sleep(60)
        # advertisements are unregistered on __exit__
    """

    def __init__(self, adapter: str | None = None) -> None:
        """
        adapter: explicit BlueZ adapter path (e.g. "/org/bluez/hci0").
                 Pass None to auto-select the first adapter that supports LE advertising.
        """
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SystemBus()
        self._adapter_path = adapter
        self._mainloop = GLib.MainLoop()
        self._thread: threading.Thread | None = None
        self._ads: list[Advertisement] = []
        self._counter = 0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the GLib mainloop thread. Called automatically by register()."""
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._mainloop.run, daemon=True, name="heraldo-mainloop")
        self._thread.start()

    def stop(self) -> None:
        """Unregister all active advertisements and stop the mainloop."""
        for ad in list(self._ads):
            self._unregister(ad)
        self._mainloop.quit()

    def __enter__(self) -> "Advertiser":
        self.start()
        return self

    def __exit__(self, *_) -> None:
        self.stop()

    # ------------------------------------------------------------------
    # Advertisement management
    # ------------------------------------------------------------------

    def register(self, beacon: Beacon, ad_type: str = "broadcast") -> Advertisement:
        """
        Register a beacon advertisement with BlueZ.

        ad_type: "broadcast" (non-connectable) or "peripheral" (connectable).
        Returns the Advertisement handle, which can be passed to unregister().
        """
        self.start()

        ad = Advertisement(self._bus, self._counter, beacon, ad_type)
        self._counter += 1

        done = threading.Event()
        outcome: list = []

        def on_success():
            outcome.append(None)
            done.set()

        def on_error(e):
            outcome.append(e)
            done.set()

        self._ad_manager().RegisterAdvertisement(
            ad.path,
            {},
            reply_handler=on_success,
            error_handler=on_error,
        )

        if not done.wait(timeout=_REPLY_TIMEOUT):
            raise AdvertisementError("Timed out waiting for BlueZ to acknowledge registration")

        if outcome[0] is not None:
            raise AdvertisementError(f"RegisterAdvertisement failed: {outcome[0]}") from outcome[0]

        self._ads.append(ad)
        return ad

    def set_alias(self, name: str) -> None:
        """Set the Bluetooth adapter's visible name (overrides the system hostname)."""
        adapter = self._bus.get_object(_BLUEZ_SERVICE, self._find_adapter())
        props = dbus.Interface(adapter, _DBUS_PROP_IFACE)
        props.Set("org.bluez.Adapter1", "Alias", dbus.String(name))

    def unregister(self, ad: Advertisement) -> None:
        """Unregister a previously registered advertisement."""
        self._unregister(ad)

    def _unregister(self, ad: Advertisement) -> None:
        done = threading.Event()

        def on_done(*_):
            if ad in self._ads:
                self._ads.remove(ad)
            done.set()

        try:
            self._ad_manager().UnregisterAdvertisement(
                ad.path,
                reply_handler=on_done,
                error_handler=on_done,
            )
            done.wait(timeout=_REPLY_TIMEOUT)
        except dbus.DBusException:
            if ad in self._ads:
                self._ads.remove(ad)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_adapter(self) -> str:
        if self._adapter_path:
            return self._adapter_path

        om = dbus.Interface(
            self._bus.get_object(_BLUEZ_SERVICE, "/"), _DBUS_OM_IFACE
        )
        for path, interfaces in om.GetManagedObjects().items():
            if _LE_ADVERTISING_MANAGER_IFACE in interfaces:
                return str(path)

        raise BlueZNotAvailableError(
            "No BLE adapter with LEAdvertisingManager1 found. "
            "Is BlueZ running and an adapter available?"
        )

    def _ad_manager(self) -> dbus.Interface:
        return dbus.Interface(
            self._bus.get_object(_BLUEZ_SERVICE, self._find_adapter()),
            _LE_ADVERTISING_MANAGER_IFACE,
        )
