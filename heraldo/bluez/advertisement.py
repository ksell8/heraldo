import dbus
import dbus.service

from ..beacons.base import Beacon

_LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
_DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
_PATH_BASE = "/org/heraldo/advertisement"


class Advertisement(dbus.service.Object):
    """
    DBus service object implementing org.bluez.LEAdvertisement1.

    BlueZ calls GetAll on this object when RegisterAdvertisement is invoked,
    so the GLib mainloop must be running before registration.
    """

    def __init__(self,
                 bus: dbus.Bus,
                 index: int,
                 beacon: Beacon,
                 ad_type: str) -> None:
        self.path = f"{_PATH_BASE}{index}"
        super().__init__(bus, self.path)
        self._beacon = beacon
        self._ad_type = ad_type

    def _properties(self) -> dict:
        props: dict = {"Type": dbus.String(self._ad_type)}

        service_uuids = self._beacon.get_service_uuids()
        if service_uuids:
            props["ServiceUUIDs"] = dbus.Array(
                [dbus.String(u) for u in service_uuids], signature="s"
            )

        manufacturer_data = self._beacon.get_manufacturer_data()
        if manufacturer_data:
            props["ManufacturerData"] = dbus.Dictionary(
                {
                    dbus.UInt16(company_id): dbus.Array(
                        [dbus.Byte(b) for b in data], signature="y"
                    )
                    for company_id, data in manufacturer_data.items()
                },
                signature="qv",
            )

        service_data = self._beacon.get_service_data()
        if service_data:
            props["ServiceData"] = dbus.Dictionary(
                {
                    dbus.String(uuid): dbus.Array(
                        [dbus.Byte(b) for b in data], signature="y"
                    )
                    for uuid, data in service_data.items()
                },
                signature="sv",
            )

        local_name = self._beacon.get_local_name()
        if local_name is not None:
            props["LocalName"] = dbus.String(local_name)

        return props

    @dbus.service.method(_DBUS_PROP_IFACE, in_signature="ss", out_signature="v")
    def Get(self, interface: str, prop: str):
        if interface != _LE_ADVERTISEMENT_IFACE:
            raise dbus.DBusException(f"No such interface: {interface}")
        return self._properties()[prop]

    @dbus.service.method(_DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface: str):
        if interface != _LE_ADVERTISEMENT_IFACE:
            raise dbus.DBusException(f"No such interface: {interface}")
        return self._properties()

    @dbus.service.method(_LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        """Called by BlueZ when the advertisement is unregistered."""
