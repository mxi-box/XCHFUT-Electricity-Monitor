"""Sebsor for xchfut_electricity_monitor integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.const import ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_MONETARY, DEVICE_CLASS_ENERGY
from homeassistant.components.sensor import STATE_CLASS_TOTAL_INCREASING, SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .const import CNY_PER_KWH
from .const import CONF_ROOMID
from .api import api

_LOGGER = logging.getLogger(__name__)


SCAN_INTERVAL = timedelta(seconds=600)


async def async_setup_entry(
    hass : HomeAssistant, 
    config_entry : ConfigType, 
    async_add_devices : AddEntitiesCallback
    ):
    roomid = config_entry.data[CONF_ROOMID]
    consume = ElectricityConsumeSensor(roomid)
    deposit = ElectricityDepositSensor(roomid, consume)

    async_add_devices([deposit, consume], True)
    return True


class ElectricityDepositSensor(SensorEntity):
    def __init__(self, roomid : str, consume : ElectricityConsumeSensor) -> None:
        self._state = None
        self._roomid = roomid
        self._consume = consume

    @property
    def unique_id(self) -> str:
        return "ElecDeposit." + self._roomid
    
    @property
    def name(self) -> str:
        return "ElecDeposit_" + self._roomid

    @property
    def state(self) -> float:
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        return '¥'
    
    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_MONETARY
    
    async def async_update(self) -> None:
        try:
            self._state = float(await api.query_electricity_deposite(self._roomid))

            if self._consume.last_state and self._state < self._consume.last_state:
                self._consume._state += (self._consume.last_state - self._state) / CNY_PER_KWH
                self._consume.async_write_ha_state()
            
            self._consume.last_state = self._state

        except Exception as e:
            _LOGGER.exception(e)


class ElectricityConsumeSensor(SensorEntity):
    def __init__(self, roomid : str) -> None:
        self._state = 0.0
        self.last_state = None
        self._roomid = roomid

    @property
    def unique_id(self) -> str:
        return "ElecConsume." + self._roomid
    
    @property
    def name(self) -> str:
        return "ElecConsume_" + self._roomid
        
    @property
    def state(self) -> float:
        return self._state

    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_ENERGY

    @property
    def unit_of_measurement(self) -> str:
        return ENERGY_KILO_WATT_HOUR

    @property
    def state_class(self) -> str:
        return STATE_CLASS_TOTAL_INCREASING
    
    @property
    def should_poll(self) -> bool:
        return False
