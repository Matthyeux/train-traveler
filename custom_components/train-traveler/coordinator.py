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
from homeassistant.const import CONF_SCAN_INTERVAL

from .const import DOMAIN, CONF_START_AREA, CONF_END_AREA, CONF_JOURNEYS_COUNT, CONF_AREA_LABEL, CONF_AREA_COORD, CONF_AREA_ID, CONF_AREA_NAME

from sncf.repositories.repository_manager import ApiRepository
from sncf.repositories.journey_repository import ApiJourneyRepository 
from sncf.repositories.stop_area_repository import ApiStopAreaRepository
from sncf.repositories.disruption_repository import ApiDisruptionRepository


from sncf.connections.connection_manager import ApiConnectionManager
from sncf.services.journey_service import JourneyService

from sncf.models.area_model import Area


_LOGGER = logging.getLogger(__name__)

class JourneyCoordinator(DataUpdateCoordinator):

    def __init__(self, connection: ApiConnectionManager, hass: HomeAssistant, entry: ConfigEntry, last_journey: bool = False):
        self.config = entry.data
        
        # set update_interval to 6hours if we are going to fetch last journey (to reduce useless api call)
        update_interval = 21600
        if not last_journey:
            update_interval = self.config[CONF_SCAN_INTERVAL]

        super().__init__(
            hass,
            _LOGGER,
            name="Journey",
            update_interval=timedelta(seconds=update_interval)
        )
        
        self.last_journey = last_journey
        self.connection = connection
        self.hass = hass
        self.entry = entry
        self.repository_manager = ApiRepository(self.connection)
        self.journey_service: JourneyService.JourneyService = JourneyService(
            stop_area_repository=ApiStopAreaRepository(self.connection),
            journey_repository=ApiJourneyRepository(self.connection),
            disruption_repository=ApiDisruptionRepository(self.connection)
        )

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

                _LOGGER.debug("Api calls count %s", self.repository_manager._query_count)
                
                _LOGGER.info("data sucessfully fetched")
                return journeys
        except Exception as err:
            _LOGGER.error("Failed to fetch API : %s", err)
            raise UpdateFailed(f"Error fetching api data: {err}")
        
    