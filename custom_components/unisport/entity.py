"""BlueprintEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import UnisportDataUpdateCoordinator

if TYPE_CHECKING:
    from .data import UnisportLocation


class UnisportEntity(CoordinatorEntity[UnisportDataUpdateCoordinator]):
    """UnisportEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: UnisportDataUpdateCoordinator,
        location: UnisportLocation,
        class_: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        location_id = location.location_id
        device_id = f"{coordinator.config_entry.entry_id}-{location_id}"
        self._attr_unique_id = f"{device_id}-{class_}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (coordinator.config_entry.domain, device_id),
            },
            name=f"Unisport {location.name}",
            serial_number=f"unisport-location-{location_id}",
            manufacturer="Unisport",
            model="Gym",
        )
        self._location_id = location_id

    def _get_location(self) -> UnisportLocation | None:
        locations = self.coordinator.data.get("locations")
        if locations is None:
            return None
        return locations.get(self._location_id)
