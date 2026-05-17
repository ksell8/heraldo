from abc import ABC, abstractmethod


class Beacon(ABC):
    """
    Abstract base for BLE beacon advertisement payloads.

    Subclasses populate whichever BlueZ LEAdvertisement1 properties they need.
    At minimum, implement get_manufacturer_data() or get_service_data().
    """

    def get_manufacturer_data(self) -> dict[int, bytes]:
        """Map of {company_id: payload_bytes} for ManufacturerData."""
        return {}

    def get_service_uuids(self) -> list[str]:
        """List of 16/32/128-bit UUIDs to include in ServiceUUIDs."""
        return []

    def get_service_data(self) -> dict[str, bytes]:
        """Map of {uuid: payload_bytes} for ServiceData."""
        return {}

    def get_local_name(self) -> str | None:
        """Optional LocalName to include in the advertisement."""
        return None
