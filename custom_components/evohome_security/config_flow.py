"""Config flow for EvoHome Security integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

# Import from parent directory (the repository root)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from evohome_security import EvoHomeSecurityClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "evohome_security"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # Create client and test authentication
    client = EvoHomeSecurityClient(
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD]
    )

    try:
        # Run authentication in executor since it's blocking I/O
        auth_result = await hass.async_add_executor_job(client.authenticate)
        
        if not auth_result:
            raise InvalidAuth
        
        # Clean up
        await hass.async_add_executor_job(client.close)
        
        # Return info that you want to store in the config entry.
        return {"title": f"EvoHome Security ({data[CONF_USERNAME]})"}
    
    except Exception as exc:
        _LOGGER.error("Error validating credentials: %s", exc)
        await hass.async_add_executor_job(client.close)
        raise InvalidAuth from exc


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EvoHome Security."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on username to prevent duplicates
                await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
