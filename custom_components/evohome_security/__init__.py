"""The EvoHome Security integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

# Import from the component directory
from .evohome_security import EvoHomeSecurityClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "evohome_security"
PLATFORMS: list[Platform] = [Platform.ALARM_CONTROL_PANEL]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EvoHome Security from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create the client
    client = EvoHomeSecurityClient(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD]
    )

    # Test authentication
    try:
        auth_result = await hass.async_add_executor_job(client.authenticate)
        if not auth_result:
            raise ConfigEntryNotReady("Failed to authenticate with EvoHome Security")
    except Exception as err:
        _LOGGER.error("Error authenticating with EvoHome Security: %s", err)
        await hass.async_add_executor_job(client.close)
        raise ConfigEntryNotReady from err

    # Store the client
    hass.data[DOMAIN][entry.entry_id] = client

    # Forward the setup to the alarm_control_panel platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Close the client
        client = hass.data[DOMAIN].pop(entry.entry_id)
        await hass.async_add_executor_job(client.close)

    return unload_ok
