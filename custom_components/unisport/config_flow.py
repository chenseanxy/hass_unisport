"""Adds config flow for Blueprint."""

from __future__ import annotations

from homeassistant import config_entries
from slugify import slugify

from .const import DOMAIN, LOGGER


class UnisportFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Unisport."""

    VERSION = 1

    async def async_step_user(
        self,
        _: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        LOGGER.debug("Setting up unisport")
        await self.async_set_unique_id(
            ## Do NOT use this in production code
            ## The unique_id should never be something that can change
            ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
            unique_id=slugify("unisport"),
        )
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="Unisport",
            data={},
        )
