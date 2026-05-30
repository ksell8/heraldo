import struct

from .base import Beacon

# Eddystone Service UUID (16-bit: 0xFEAA, as a 128-bit GATT UUID string)
EDDYSTONE_UUID = "0000feaa-0000-1000-8000-00805f9b34fb"

# Eddystone frame types
_FRAME_TYPE_UID = 0x00


class Eddystone(Beacon):
    """
    Eddystone-UID beacon advertisement payload.

    Advertises as service data under the Eddystone service UUID (0xFEAA).
    This format is natively recognized by Android and generic BLE scanners
    (including nRF Connect) without any special UUID knowledge.

    namespace: 10-byte hex string (e.g. "6469737475726274a865")
    instance:  6-byte hex string  (e.g. "737461747573")
    tx_power:  calibrated RSSI at 1 metre (signed, default -59 dBm)

    See: https://github.com/google/eddystone/tree/master/eddystone-uid
    """

    def __init__(
        self,
        namespace: str,
        instance: str,
        tx_power: int = -59,
    ) -> None:
        ns_bytes = bytes.fromhex(namespace)
        inst_bytes = bytes.fromhex(instance)

        if len(ns_bytes) != 10:
            raise ValueError(f"namespace must be 10 bytes (20 hex chars), got {len(ns_bytes)}")
        if len(inst_bytes) != 6:
            raise ValueError(f"instance must be 6 bytes (12 hex chars), got {len(inst_bytes)}")
        if not (-128 <= tx_power <= 127):
            raise ValueError(f"tx_power must be -128–127 dBm, got {tx_power}")

        self.namespace = ns_bytes
        self.instance = inst_bytes
        self.tx_power = tx_power

    def get_service_uuids(self) -> list[str]:
        return [EDDYSTONE_UUID]

    def get_service_data(self) -> dict[str, bytes]:
        # Frame layout (18 bytes total):
        #   1B frame type (0x00)
        #   1B tx_power (signed)
        #  10B namespace
        #   6B instance
        payload = struct.pack(
            ">Bb10s6s",
            _FRAME_TYPE_UID,
            self.tx_power,
            self.namespace,
            self.instance,
        )
        return {EDDYSTONE_UUID: payload}

    def __repr__(self) -> str:
        return (
            f"EddystoneUID(namespace={self.namespace.hex()}, "
            f"instance={self.instance.hex()}, tx_power={self.tx_power})"
        )