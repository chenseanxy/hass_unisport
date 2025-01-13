"""Binary sensor platform for unisport."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import UnisportEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import UnisportDataUpdateCoordinator
    from .data import UnisportConfigEntry, UnisportLocation


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: UnisportConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        UnisportOpenStatusSensor(
            coordinator=coordinator,
            location=location,
        )
        for location in coordinator.data.get("locations", {}).values()
    )


class UnisportOpenStatusSensor(UnisportEntity, BinarySensorEntity):
    """Unisport Open Status Sensor class."""

    def __init__(
        self,
        coordinator: UnisportDataUpdateCoordinator,
        location: UnisportLocation,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, location, "open_status")
        self.entity_description = BinarySensorEntityDescription(
            key=f"unisport-open-status-{location.location_id}",
            name=f"Unisport {location.name} Status",
            icon="mdi:door",
            device_class=BinarySensorDeviceClass.OPENING,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary_sensor is on."""
        loc = self._get_location()
        if loc is None:
            return None
        return loc.is_open_now()
