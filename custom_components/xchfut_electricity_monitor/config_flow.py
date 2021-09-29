"""Config flow for xchfut_electricity_monitor integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .const import CONF_ROOMID
from .api import ConnectFail
from .api import FetchFail
from .api import api

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ROOMID): str
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for xchfut_electricity_monitor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        await self.async_set_unique_id(user_input[CONF_ROOMID])
        self._abort_if_unique_id_configured()

        errors = {}

        try:
            info = await api.query_electricity_deposite(user_input[CONF_ROOMID])
        except ConnectFail:
            errors["base"] = "cannot_connect"
        except FetchFail:
            errors["base"] = "fetch_fail"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title='Electricity.' + user_input[CONF_ROOMID], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
