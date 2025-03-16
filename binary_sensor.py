"""Support for Smarthomesec Security System binary sensors."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, TYPE_CLASS_BINARY_SENSOR
from .base_entity import SmarthomesecBaseSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a binary sensors for a Smarthomesec device."""

    coord = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    devices = hass.data[DOMAIN][config_entry.entry_id]["binary_sensor_devices"]

    async_add_entities(
        SmarthomesecBinarySensor(coord, device, config_entry.entry_id) for device in devices
    )


class SmarthomesecBinarySensor(SmarthomesecBaseSensor, BinarySensorEntity):
    """A binary sensor implementation for Smarthomesec device."""

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        if len(self._device["status_open"]):
            return (self._device["status_open"][0] == "device_status.dc_open")
        elif self._device["status_motion"]:
            return (self._device["status_motion"] == "1")

    @property
    def device_class(self) -> BinarySensorDeviceClass | None:
        """Return the class of the binary sensor."""
        return TYPE_CLASS_BINARY_SENSOR[self._device["type"]]
