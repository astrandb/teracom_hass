"""Binary sensors."""

from .const import TCW122B_CM, TCW181B_CM, TCW241
from .entity import TcwEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the binary sensors."""

    def get_entities():
        sensors = []
        if config_entry.data["model"] == TCW122B_CM:
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital1",
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
                    None,
                    None,
                    None,
                )
            )
        elif config_entry.data["model"] == TCW181B_CM:
            sensors.append(
                TcwBinarySensor(
                    hass,
                    config_entry,
                    "digital",
                    None,
                    None,
                    None,
                )
            )
        elif config_entry.data["model"] in (TCW241,):
            for i in range(1, 5):
                sensors.append(
                    TcwBinarySensor(
                        hass,
                        config_entry,
                        f"digital{i}",
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
