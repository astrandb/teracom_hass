"""Buttons for Teracom devices."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import TCW
from .entity import TcwEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the entry."""

    def get_entities():
        entities = []
        if config_entry.data["model"] in (TCW.TCW220, TCW.TCW122B_CM):
            nrx = range(1, 3)
        elif config_entry.data["model"] == TCW.TCW181B_CM:
            nrx = range(1, 9)
        elif config_entry.data["model"] in (TCW.TCW241, TCW.TCW242):
            nrx = range(1, 5)
        else:
            return entities
        if config_entry.data["model"] in (TCW.TCW122B_CM, TCW.TCW181B_CM):
            entities.extend(
                [
                    TcwButton(
                        hass,
                        config_entry,
                        f"relay{nox}",
                        None,
                        None,
                        None,
                    )
                    for nox in nrx
                ]
            )
        if config_entry.data["model"] in (TCW.TCW220, TCW.TCW241, TCW.TCW242):
            entities.extend(
                [
                    TcwButtonGen2(
                        hass,
                        config_entry,
                        f"relay{nox}",
                        None,
                        None,
                        None,
                    )
                    for nox in nrx
                ]
            )
        return entities

    async_add_entities(get_entities())


class TcwButton(TcwEntity, ButtonEntity):
    """Representation of a button."""

    async def async_press(self, **kwargs):
        """Press the button."""
        _LOGGER.debug("Pulse relay %s", self.name)
        await self._data["api"].pulse_relay(self._data_key[-1])
        self._data[self._data_key] = True


class TcwButtonGen2(TcwEntity, ButtonEntity):
    """Representation of a button (Gen2)."""

    async def async_press(self, **kwargs):
        """Press the button."""
        _LOGGER.debug("Pulse relay Gen2 %s", self.name)
        await self._data["api"].pulse_relay_g2(relay_no=self._data_key[-1])
        self._data[self._data_key] = True
