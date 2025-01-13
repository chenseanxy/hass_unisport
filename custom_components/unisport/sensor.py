"""Sensor platform for integration_blueprint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass

from .entity import UnisportEntity

if TYPE_CHECKING:
    import datetime

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import UnisportDataUpdateCoordinator
    from .data import UnisportConfigEntry, UnisportLocation


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: UnisportConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        Sensor(
            coordinator=coordinator,
            location=location,
        )
        for Sensor in [
            UnisportVisitorsSensor,
            UnisportCapacitySensor,
            UnisportTodayOpenSensor,
            UnisportTodayCloseSensor,
        ]
        for location in coordinator.data.get("locations", {}).values()
    )


class UnisportVisitorsSensor(UnisportEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    def __init__(
        self,
        coordinator: UnisportDataUpdateCoordinator,
        location: UnisportLocation,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, location, "visitors")
        self.entity_description = SensorEntityDescription(
            key=f"unisport-visitors-{location.location_id}",
            name=f"Unisport {location.name} Visitors",
            icon="mdi:account",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=0,
        )

    @property
    def native_value(self) -> int | None:
        """Return the native value of the sensor."""
        return self.coordinator.data.get("live_validations", {}).get(
            self._location_id, 0
        )


class UnisportCapacitySensor(UnisportEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    def __init__(
        self,
        coordinator: UnisportDataUpdateCoordinator,
        location: UnisportLocation,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, location, "capacity")
        self.entity_description = SensorEntityDescription(
            key=f"unisport-capacity-{location.location_id}",
            name=f"Unisport {location.name} Capacity",
            icon="mdi:account-multiple",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=0,
        )

    @property
    def native_value(self) -> int | None:
        """Return the native value of the sensor."""
        loc = self._get_location()
        return loc.max_capacity if loc else None


class UnisportTodayOpenSensor(UnisportEntity, SensorEntity):
    """Unisport Opening Time Sensor class."""

    def __init__(
        self,
        coordinator: UnisportDataUpdateCoordinator,
        location: UnisportLocation,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, location, "today_open")
        self.entity_description = SensorEntityDescription(
            key=f"unisport-today-open-{location.location_id}",
            name=f"Unisport {location.name} Opening Time Today",
            icon="mdi:clock",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_registry_enabled_default=False,
        )

    @property
    def native_value(self) -> datetime.datetime | None:
        """Return the native value of the sensor."""
        loc = self._get_location()
        if not loc:
            return None
        opening_hours = loc.get_opening_hour_today()
        if not opening_hours:
            return None
        return opening_hours[0]


class UnisportTodayCloseSensor(UnisportEntity, SensorEntity):
    """Unisport Closing Time Sensor class."""

    def __init__(
        self,
        coordinator: UnisportDataUpdateCoordinator,
        location: UnisportLocation,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, location, "today_close")
        self.entity_description = SensorEntityDescription(
            key=f"unisport-today-close-{location.location_id}",
            name=f"Unisport {location.name} Closing Time Today",
            icon="mdi:clock",
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_registry_enabled_default=False,
        )

    @property
    def native_value(self) -> datetime.datetime | None:
        """Return the native value of the sensor."""
        loc = self._get_location()
        if not loc:
            return None
        opening_hours = loc.get_opening_hour_today()
        if not opening_hours:
            return None
        return opening_hours[1]
