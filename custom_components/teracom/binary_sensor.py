"""Binary sensors"""

from .entity import TcwEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the binary sensors."""

    def get_entities():
        sensors = []
        if config_entry.data["model"] == "TCW122B-CM":
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital1",
                    "dig1",
                    "Digital Input 1",
                    None,
                    None,
                    None,
                )
            )
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital2",
                    "dig2",
                    "Digital Input 2",
                    None,
                    None,
                    None,
                )
            )
        elif config_entry.data["model"] == "TCW181B-CM":
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital",
                    "dig",
                    "Digital Input",
                    None,
                    None,
                    None,
                )
            )
        return sensors

    async_add_entities(await hass.async_add_job(get_entities), True)


class TcwBinarySensor(TcwEntity):
    """Representation of a sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._data.get(self._data_key)
