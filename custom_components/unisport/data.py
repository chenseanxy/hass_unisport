"""Custom types for integration_blueprint."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel

from .const import LOGGER, UNISPORT_TZ

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import UnisportApiClient
    from .coordinator import UnisportDataUpdateCoordinator


type UnisportConfigEntry = ConfigEntry[UnisportData]


@dataclass
class UnisportData:
    """Data for the Blueprint integration."""

    client: UnisportApiClient
    coordinator: UnisportDataUpdateCoordinator
    integration: Integration


class UnisportLocationOpeningHour(BaseModel):
    """Opening hours for a location."""

    time_start: str
    time_end: str


class UnisportLocation(BaseModel):
    """Locations field of the response of the `populartimes` endpoint."""

    location_id: int
    name: str
    max_capacity: int
    opening_hours: dict[int, UnisportLocationOpeningHour]

    def get_opening_hour_today(
        self,
    ) -> tuple[datetime.datetime, datetime.datetime] | None:
        """Get the opening hours for today."""
        today = datetime.datetime.now(tz=UNISPORT_TZ).today()
        # opening_hours has 1-based index
        opening_hour = self.opening_hours.get(today.weekday() + 1)
        if not opening_hour:
            LOGGER.debug(
                "No opening hours for today: %s, weekday: %s, available: %s",
                today,
                today.weekday(),
                self.opening_hours,
            )
            return None
        times = (
            # Opening
            UNISPORT_TZ.localize(
                datetime.datetime.combine(
                    today,
                    datetime.time.fromisoformat(opening_hour.time_start),
                ),
            ),
            # Closing
            UNISPORT_TZ.localize(
                datetime.datetime.combine(
                    today,
                    datetime.time.fromisoformat(opening_hour.time_end),
                )
                if not opening_hour.time_end.startswith("24:")
                # 24:00 is not a valid time, so we need to convert it to 00:00 the next day
                else datetime.datetime.combine(
                    today + datetime.timedelta(days=1),
                    datetime.time(0, 0),
                ),
            ),
        )
        LOGGER.debug(
            "Updating opening hour, original: %s -> parsed: %s", opening_hour, times
        )
        return times

    def is_open_now(self) -> bool | None:
        """Return if the location is open now."""
        opening_hours = self.get_opening_hour_today()
        if not opening_hours:
            return None
        now = datetime.datetime.now(tz=UNISPORT_TZ)
        return opening_hours[0] <= now <= opening_hours[1]


class UnisportResponse(BaseModel):
    """Response of the `populartimes` endpoint."""

    # Key for these fields: location id
    live_validations: dict[int, int]
    locations: dict[int, UnisportLocation]
