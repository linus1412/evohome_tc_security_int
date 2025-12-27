"""Support for EvoHome Security alarm control panel."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Import from the component directory
from .evohome_security import AlarmState, EvoHomeSecurityClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "evohome_security"

# Polling interval (in seconds)
SCAN_INTERVAL = 30


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the EvoHome Security alarm control panel."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EvoHomeAlarmControlPanel(client, entry)])


class EvoHomeAlarmControlPanel(AlarmControlPanelEntity):
    """Representation of an EvoHome Security alarm control panel."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )

    def __init__(self, client: EvoHomeSecurityClient, entry: ConfigEntry) -> None:
        """Initialize the alarm control panel."""
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_alarm"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "EvoHome Security System",
            "manufacturer": "Total Connect",
            "model": "EvoHome Security",
        }
        self._attr_state = None

    async def async_update(self) -> None:
        """Update the state of the alarm."""
        try:
            # Get status from client (run in executor since it's blocking)
            alarm_state = await self.hass.async_add_executor_job(
                self._client.get_status
            )

            # Map to Home Assistant states
            if alarm_state == AlarmState.DISARMED:
                self._attr_state = STATE_ALARM_DISARMED
            elif alarm_state == AlarmState.ARMED_HOME:
                self._attr_state = STATE_ALARM_ARMED_HOME
            elif alarm_state == AlarmState.ARMED_AWAY:
                self._attr_state = STATE_ALARM_ARMED_AWAY
            else:
                self._attr_state = None
                _LOGGER.warning("Unknown alarm state received")

        except Exception as err:
            _LOGGER.error("Error updating alarm state: %s", err)
            self._attr_state = None

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        try:
            result = await self.hass.async_add_executor_job(self._client.disarm)
            if result:
                _LOGGER.info("Successfully disarmed alarm")
                await self.async_update()
            else:
                _LOGGER.error("Failed to disarm alarm")
        except NotImplementedError:
            _LOGGER.warning("Disarm functionality not yet implemented in evosec2.py")
        except Exception as err:
            _LOGGER.error("Error disarming alarm: %s", err)

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        try:
            result = await self.hass.async_add_executor_job(self._client.arm_home)
            if result:
                _LOGGER.info("Successfully armed alarm (home)")
                await self.async_update()
            else:
                _LOGGER.error("Failed to arm alarm (home)")
        except NotImplementedError:
            _LOGGER.warning("Arm home functionality not yet implemented in evosec2.py")
        except Exception as err:
            _LOGGER.error("Error arming alarm (home): %s", err)

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        try:
            result = await self.hass.async_add_executor_job(self._client.arm_away)
            if result:
                _LOGGER.info("Successfully armed alarm (away)")
                await self.async_update()
            else:
                _LOGGER.error("Failed to arm alarm (away)")
        except NotImplementedError:
            _LOGGER.warning("Arm away functionality not yet implemented in evosec2.py")
        except Exception as err:
            _LOGGER.error("Error arming alarm (away): %s", err)
