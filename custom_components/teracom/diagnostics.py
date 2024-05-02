"""Diagnostics support for Teracom."""

from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {CONF_USERNAME, CONF_PASSWORD}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""

    return {
        "config_entry_data": async_redact_data(dict(config_entry.data), TO_REDACT),
        "data": async_redact_data(
            hass.data[DOMAIN][config_entry.entry_id]["data_dict"], TO_REDACT
        ),
    }
