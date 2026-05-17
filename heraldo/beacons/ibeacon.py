import struct
import uuid as _uuid

from .base import Beacon

APPLE_COMPANY_ID = 0x004C

# iBeacon subtype (0x02) and payload length (0x15 = 21: 16 UUID + 2 major + 2 minor + 1 tx_power)
_IBEACON_TYPE = 0x02
_IBEACON_LENGTH = 0x15


class IBeacon(Beacon):
    """
    Apple iBeacon advertisement payload.

    Advertises as manufacturer-specific data under Apple's company ID (0x004C).
    tx_power should be calibrated to the measured RSSI at 1 metre from the device.
    """

    def __init__(
        self,
        uuid: str,
        major: int,
        minor: int,
        tx_power: int = -59,
    ) -> None:
        if not (0 <= major <= 0xFFFF):
            raise ValueError(f"major must be 0–65535, got {major}")
        if not (0 <= minor <= 0xFFFF):
            raise ValueError(f"minor must be 0–65535, got {minor}")
        if not (-128 <= tx_power <= 127):
            raise ValueError(f"tx_power must be -128–127 dBm, got {tx_power}")

        self.uuid = _uuid.UUID(uuid)
        self.major = major
        self.minor = minor
        self.tx_power = tx_power

    def get_manufacturer_data(self) -> dict[int, bytes]:
        payload = struct.pack(
            ">BB16sHHb",
            _IBEACON_TYPE,
            _IBEACON_LENGTH,
            self.uuid.bytes,  # UUID in big-endian (network) byte order
            self.major,
            self.minor,
            self.tx_power,
        )
        return {APPLE_COMPANY_ID: payload}

    def __repr__(self) -> str:
        return (
            f"IBeacon(uuid={self.uuid!s}, major={self.major}, "
            f"minor={self.minor}, tx_power={self.tx_power})"
        )
