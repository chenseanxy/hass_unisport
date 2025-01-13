"""Constants for integration_blueprint."""

from logging import Logger, getLogger

import pytz

LOGGER: Logger = getLogger(__package__)

DOMAIN = "unisport"
ATTRIBUTION = "Data from unisport.fi"

UNISPORT_TZ_NAME = "Europe/Helsinki"
UNISPORT_TZ = pytz.timezone(UNISPORT_TZ_NAME)

STATE_OPEN = "open"
STATE_CLOSED = "closed"
