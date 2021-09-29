"""Sebsor for xchfut_electricity_monitor integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN
from .const import CONF_ROOMID
from .api import api

_LOGGER = logging.getLogger(__name__)


SCAN_INTERVAL = timedelta(seconds=600)


async def async_setup_entry(hass, config_entry, async_add_devices):
    async_add_devices([ElectricitySensor(config_entry.data[CONF_ROOMID])], True)
    return True


class ElectricitySensor(SensorEntity):
    def __init__(self, roomid : str) -> None:
        self._state = None
        self.roomid = roomid

    @property
    def name(self) -> str:
        return "elec." + self.roomid
    
    @property
    def state(self) -> float:
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        return '￥'
    
    async def async_update(self) -> None:
        try:
            self._state = float(
            await api.query_electricity_deposite(self.roomid)
            )
        except Exception as e:
            _LOGGER.exception(e)
