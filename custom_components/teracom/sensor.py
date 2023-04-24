"""Sensors"""
#  import logging
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfTemperature,
)

from .const import DOMAIN, TCW122B_CM, TCW241, TCW242
from .entity import TcwEntity

#  _LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the entry."""

    def get_entities():
        sensors = []
        if config_entry.data["model"] == TCW122B_CM:
            for i in range(1, 3):
                sensors.append(
                    TcwSensor(
                        hass,
                        config_entry,
                        f"temperature{i}",
                        SensorDeviceClass.TEMPERATURE,
                        SensorStateClass.MEASUREMENT,
                        UnitOfTemperature.CELSIUS,
                    )
                )
            for i in range(1, 3):
                sensors.append(
                    TcwSensor(
                        hass,
                        config_entry,
                        f"humidity{i}",
                        SensorDeviceClass.HUMIDITY,
                        SensorStateClass.MEASUREMENT,
                        PERCENTAGE,
                    )
                )
            for i in range(1, 3):
                sensors.append(
                    TcwSensor(
                        hass,
                        config_entry,
                        f"voltage{i}",
                        SensorDeviceClass.VOLTAGE,
                        SensorStateClass.MEASUREMENT,
                        UnitOfElectricPotential.VOLT,
                    )
                )

        if config_entry.data["model"] in (TCW241,):
            for i in range(1, 5):
                sensors.append(
                    TcwSensor(
                        hass,
                        config_entry,
                        f"analog{i}",
                        SensorDeviceClass.VOLTAGE,
                        SensorStateClass.MEASUREMENT,
                        UnitOfElectricPotential.VOLT,
                    )
                )
            for i in range(1, 9):
                device_class = None
                native_unit = None
                state_class = None
                if (
                    hass.data[DOMAIN][config_entry.entry_id]["data_dict"]["Monitor"][
                        "S"
                    ][f"S{i}"]["item1"]["unit"]
                    == "°C"
                ):
                    device_class = SensorDeviceClass.TEMPERATURE
                    native_unit = UnitOfTemperature.CELSIUS
                    state_class = SensorStateClass.MEASUREMENT
                if (
                    hass.data[DOMAIN][config_entry.entry_id]["data_dict"]["Monitor"][
                        "S"
                    ][f"S{i}"]["item1"]["unit"]
                    == "V"
                ):
                    device_class = SensorDeviceClass.VOLTAGE
                    native_unit = UnitOfElectricPotential.VOLT
                    state_class = SensorStateClass.MEASUREMENT
                if (
                    hass.data[DOMAIN][config_entry.entry_id]["data_dict"]["Monitor"][
                        "S"
                    ][f"S{i}"]["item1"]["unit"]
                    == "A"
                ):
                    device_class = SensorDeviceClass.CURRENT
                    native_unit = UnitOfElectricCurrent.AMPERE
                    state_class = SensorStateClass.MEASUREMENT
                sensors.append(
                    TcwSensor(
                        hass,
                        config_entry,
                        f"sensor{i}",
                        device_class,
                        state_class,
                        native_unit,
                    )
                )
                device_class = None
                native_unit = None
                state_class = None
                if (
                    hass.data[DOMAIN][config_entry.entry_id]["data_dict"]["Monitor"][
                        "S"
                    ][f"S{i}"]["item2"]["unit"]
                    == "%RH"
                ):
                    device_class = SensorDeviceClass.HUMIDITY
                    native_unit = PERCENTAGE
                    state_class = SensorStateClass.MEASUREMENT
                sensors.append(
                    TcwSensor(
                        hass,
                        config_entry,
                        f"sensor{i}b",
                        device_class,
                        state_class,
                        native_unit,
                    )
                )

        return sensors

    async_add_entities(await hass.async_add_job(get_entities), True)


class TcwSensor(TcwEntity, SensorEntity):
    """Representation of a sensor."""

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._data.get(self._data_key)

    @property
    def entity_registry_enabled_default(self):
        """Disable sensor if not used."""
        #  _LOGGER.debug("Enable sensor: %s", self._data[self._data_key])
        return self._data.get(self._data_key) is not None
