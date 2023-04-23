"""Sensors"""
#  import logging
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature

from .entity import TcwEntity

#  _LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the entry."""

    def get_entities():
        sensors = []
        if config_entry.data["model"] == "TCW122B-CM":
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "temperature1",
                    "temp1",
                    "Temperature 1",
                    SensorDeviceClass.TEMPERATURE,
                    SensorStateClass.MEASUREMENT,
                    UnitOfTemperature.CELSIUS,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "temperature2",
                    "temp2",
                    "Temperature 2",
                    SensorDeviceClass.TEMPERATURE,
                    SensorStateClass.MEASUREMENT,
                    UnitOfTemperature.CELSIUS,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "humidity1",
                    "hum1",
                    "Humidity 1",
                    SensorDeviceClass.HUMIDITY,
                    SensorStateClass.MEASUREMENT,
                    PERCENTAGE,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "humidity2",
                    "hum2",
                    "Humidity 2",
                    SensorDeviceClass.HUMIDITY,
                    SensorStateClass.MEASUREMENT,
                    PERCENTAGE,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "voltage1",
                    "volt1",
                    "Voltage 1",
                    SensorDeviceClass.VOLTAGE,
                    SensorStateClass.MEASUREMENT,
                    UnitOfElectricPotential.VOLT,
                )
            )
            sensors.append(
                TcwSensor(
                    hass,
                    config_entry,
                    "voltage2",
                    "volt2",
                    "Voltage 2",
                    SensorDeviceClass.VOLTAGE,
                    SensorStateClass.MEASUREMENT,
                    UnitOfElectricPotential.VOLT,
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
        return self._data[self._data_key] is not None
