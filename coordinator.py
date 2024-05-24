from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed
)
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL, CONF_URL, CONF_REGION

from .const import DOMAIN, CONF_START_AREA, CONF_END_AREA, CONF_JOURNEYS_COUNT, CONF_AREA_LABEL, CONF_AREA_COORD, CONF_AREA_ID, CONF_AREA_NAME

from sncf.repositories.journey_repository import ApiJourneyRepository 
from sncf.repositories.stop_area_repository import ApiStopAreaRepository
from sncf.repositories.disruption_repository import ApiDisruptionRepository


from sncf.connections.connection_manager import ApiConnectionManager
from sncf.services.journey_service import JourneyService

from sncf.models.area_model import Area


_LOGGER = logging.getLogger(__name__)

class JourneyCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, last_journey: bool = False):
        self.config = entry.data
        super().__init__(
            hass,
            _LOGGER,
            name="Journey",
            update_interval=timedelta(seconds=self.config[CONF_SCAN_INTERVAL])
        )
        
        connection = ApiConnectionManager(self.config[CONF_URL], self.config[CONF_API_KEY], self.config[CONF_REGION])
        journey_service = JourneyService(
            stop_area_repository=ApiStopAreaRepository(connection),
            journey_repository=ApiJourneyRepository(connection),
            disruption_repository=ApiDisruptionRepository(connection)
        )

        self.last_journey = last_journey
        self.hass = hass
        self.entry = entry
        self.journey_service: JourneyService.JourneyService = journey_service

    async def _async_update_data(self):
        _LOGGER.info("Fetch data for journey %s", self.config[CONF_START_AREA][CONF_AREA_LABEL])
        try:
            async with async_timeout.timeout(30):
                start_area = Area(
                    self.config[CONF_START_AREA][CONF_AREA_ID], 
                    self.config[CONF_START_AREA][CONF_AREA_NAME], 
                    self.config[CONF_START_AREA][CONF_AREA_LABEL], 
                    self.config[CONF_START_AREA][CONF_AREA_COORD]
                )
                
                end_area = Area(
                    self.config[CONF_END_AREA][CONF_AREA_ID], 
                    self.config[CONF_END_AREA][CONF_AREA_NAME], 
                    self.config[CONF_END_AREA][CONF_AREA_LABEL], 
                    self.config[CONF_END_AREA][CONF_AREA_COORD]
                )
                if self.last_journey:
                    journeys = await self.hass.async_add_executor_job(
                        self.journey_service.get_last_direct_journey,
                        start_area,
                        end_area
                    )
                else:
                    journeys = await self.hass.async_add_executor_job(
                        self.journey_service.get_direct_journeys,
                        start_area,
                        end_area,
                        self.config[CONF_JOURNEYS_COUNT]
                    )

                _LOGGER.info("data sucessfully fetched")
                return journeys
        except Exception as err:
            _LOGGER.error("Failed to fetch API : %s", err)
            raise UpdateFailed(f"Error fetching api data: {err}")
        
    