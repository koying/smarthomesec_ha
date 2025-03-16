"""Provides the Smarthomesec entity for Home Assistant."""

import logging

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import callback

from . import SmarthomesecCoordinator
from .const import DOMAIN, TYPE_TRANSLATION

_LOGGER = logging.getLogger(__name__)

class SmarthomesecDevice(CoordinatorEntity):
    """Representation of a Smarthomesec device."""

    _attr_has_entity_name = True

    def __init__(self, coord: SmarthomesecCoordinator, device) -> None:
        """Initialize a sensor for Smarthomesec device."""
        _LOGGER.info(device)

        self._coord = coord
        self._device = device
        self._attr_unique_id = device["device_id"]
        self._attr_name = f'{device["device_id"]} - {device["name"]}'

        super().__init__(coord, context=self._attr_unique_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._device = self.coordinator.data["devices"][self._attr_unique_id]
        self.async_write_ha_state()

class SmarthomesecBaseSensor(SmarthomesecDevice):
    """Smarthomesec Sensor base entity."""

    def __init__(self, coord: SmarthomesecCoordinator, device, entry_id: str) -> None:
        """Initialize the SmarthomesecBaseSensor."""
        super().__init__(coord, device)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device["device_id"])},
            name=device["name"],
            manufacturer="SmartHomeSec",
            serial_number=device["device_id"],
            model=TYPE_TRANSLATION.get(device["type"], device["type"]),
        )

    def get_type_name(self) -> str:
        """Return the type of the sensor."""
        return TYPE_TRANSLATION.get(self._device["type"], self._device["type"])
