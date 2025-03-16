"""Support for Smarthomesec System alarm control panels."""

from __future__ import annotations

import logging

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
    CodeFormat,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import callback

from .const import DOMAIN
from . import SmarthomesecCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up an alarm control panel for a Smarthomesec device."""
    coord = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    alarm_areas = hass.data[DOMAIN][config_entry.entry_id]["alarm_areas"]

    async_add_entities(
        SmarthomesecAlarm(coord, area, config_entry) for area in alarm_areas
    )

class SmarthomesecAlarm(CoordinatorEntity, AlarmControlPanelEntity):
    """An alarm_control_panel implementation for Smarthomesec."""

    _attr_name = None
    _attr_code_arm_required = True
    _attr_code_format = CodeFormat.NUMBER
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )

    def __init__(
        self, coord: SmarthomesecCoordinator, alarm, entry
    ) -> None:
        """Initialize the SmarthomesecAlarm class."""
        self._alarm = alarm
        self.coord = coord
        self.area = str(alarm["area"])

        self._attr_name = f'{entry.data[CONF_NAME]} {self.area}'
        self._attr_unique_id = f'smarthomesec_{entry.data[CONF_NAME]}_{self.area}'
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data[CONF_NAME],
            manufacturer="SmartHomeSec",
        )

        super().__init__(coord, context=self._attr_unique_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._alarm = self.coordinator.data["alarms"][self.area]
        self.async_write_ha_state()

    @property
    def alarm_state(self) -> AlarmControlPanelState | None:
        """Return the state of the device."""
        if self._alarm["mode"] == "disarm":
            return AlarmControlPanelState.DISARMED
        elif self._alarm["mode"] == "arm":
            return AlarmControlPanelState.ARMED_AWAY
        elif self._alarm["mode"] == "home":
            return AlarmControlPanelState.ARMED_HOME
        elif self._alarm["mode"] == "triggered":
            return AlarmControlPanelState.TRIGGERED
        else:
            return None

    def alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        _LOGGER.info("alarm_arm_away")
        self.coord.set_alarm_mode(self.area, "arm", code)

    def alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        _LOGGER.info("alarm_disarm")
        self.coord.set_alarm_mode(self.area, "disarm", code)

    def alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        _LOGGER.info("alarm_arm_home")
        self.coord.set_alarm_mode(self.area, "home", code)
