"""Config flow for integration."""

from json import JSONDecodeError
import logging
import requests
import hashlib
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, API_BASEHOST, API_BASEPATH

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class SmarthomesecConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Smarthomesec config flow."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            self._async_abort_entries_match(user_input)
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            try:
                await self.hass.async_add_executor_job(test_host_connection, username, password)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        """Import the yaml config."""
        self._async_abort_entries_match(
            {
                CONF_NAME: user_input[CONF_NAME],
                CONF_USERNAME: user_input[CONF_USERNAME],
                CONF_PASSWORD: user_input[CONF_PASSWORD],
            }
        )
        username = user_input[CONF_USERNAME]
        password = user_input[CONF_PASSWORD]
        try:
            await self.hass.async_add_executor_job(test_host_connection, username, password)
        except CannotConnect:
            return self.async_abort(reason="cannot_connect")
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            return self.async_abort(reason="unknown")

        return self.async_create_entry(
            title=user_input.get(CONF_NAME, "smarthomesec"),
            data={
                CONF_NAME: user_input[CONF_NAME],
                CONF_USERNAME: username,
                CONF_PASSWORD: password,
            },
        )


def test_host_connection(username: str, password: str):
    """Test if the host is reachable and is actually a Smarthomesec device."""

    try:
      payload = {
          "account": username,
          "password": hashlib.md5(password.encode('utf-8')).hexdigest(),
          "pw_encrypted": "hashed",
          "login_entry": "web"
      }
      headers = {
          "cookie": "isPrivacy=1;",
          "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
      }

      res = requests.post(f'https://{API_BASEHOST}/{API_BASEPATH}/auth/login', data=payload, headers=headers)

      if res.status_code != 200:
          raise CannotConnect(f"Status: {res.status_code}")
      
    except Exception as ex:
        _LOGGER.error("Failed to connect to SmartHomeSec: " + ex)
        raise CannotConnect from ex


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
