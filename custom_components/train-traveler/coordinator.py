from __future__ import annotations

from datetime import timedelta, datetime
import logging
import pytz

import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed
)
from homeassistant.const import CONF_SCAN_INTERVAL

from .const import (
    CONF_START_AREA, 
    CONF_END_AREA, 
    CONF_JOURNEYS_COUNT, 
    CONF_AREA_LABEL, 
    CONF_AREA_COORD, 
    CONF_AREA_ID, 
    CONF_AREA_NAME,
    CONF_PAUSE_UPDATE_EXPERIMENTAL
)

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
        self.start_area = Area(
            self.config[CONF_START_AREA][CONF_AREA_ID], 
            self.config[CONF_START_AREA][CONF_AREA_NAME], 
            self.config[CONF_START_AREA][CONF_AREA_LABEL], 
            self.config[CONF_START_AREA][CONF_AREA_COORD]
        )

        self.end_area = Area(
            self.config[CONF_END_AREA][CONF_AREA_ID], 
            self.config[CONF_END_AREA][CONF_AREA_NAME], 
            self.config[CONF_END_AREA][CONF_AREA_LABEL], 
            self.config[CONF_END_AREA][CONF_AREA_COORD]
        )

        self._timezone = pytz.timezone("Europe/Paris")
        self._pause_update = False
        self._pause_interval = None
        self._next_journeys = None

        # Added for retrocompatibility
        if not CONF_PAUSE_UPDATE_EXPERIMENTAL in self.config:
            self._conf_pause_update_experimental = False
        else:
            self._conf_pause_update_experimental = self.config[CONF_PAUSE_UPDATE_EXPERIMENTAL]

    async def _async_update_data(self):
        _LOGGER.info("Fetch data for journey %s", self.config[CONF_START_AREA][CONF_AREA_LABEL])
        try:
            async with async_timeout.timeout(30):
                if self.last_journey:
                    journeys = await self.hass.async_add_executor_job(
                        self.journey_service.get_last_direct_journey,
                        self.start_area,
                        self.end_area
                    )
                else:

                    if self._pause_update:
                        if datetime.now().astimezone(pytz.utc) > self._pause_interval.astimezone(pytz.utc):
                            _LOGGER.debug("Pause is now resumed as the next journey is in less than one hour : %s", self._pause_interval)
                            self._pause_update = False
                            self._pause_interval = None
                        else:
                            _LOGGER.debug("Update is paused because the next journey is the next day and in more than one hour : %s", self._pause_interval)
                            journeys = self._next_journeys

                    if not self._pause_update: 
                        journeys = await self.hass.async_add_executor_job(
                            self.journey_service.get_direct_journeys,
                            self.start_area,
                            self.end_area,
                            self.config[CONF_JOURNEYS_COUNT]
                        )

                        # Enable "PAUSE UPDATE" between closing time and opening time
                        if self._conf_pause_update_experimental:
                            _LOGGER.debug("Pause update configuration enabled")
                            self._next_journeys = journeys
                            next_departure_journey = self._timezone.localize(journeys.journeys[0].journey.departure_date_time).astimezone(pytz.utc)
                        
                            if next_departure_journey.date() == (datetime.now().astimezone(pytz.utc).date() + timedelta(days=1)):
                                self._pause_update = True
                                self._pause_interval = next_departure_journey - timedelta(hours=1)
                                _LOGGER.debug("Pausing update because the next journey is the next day and in more than one hour : %s", self._pause_interval)


                _LOGGER.debug("Api calls count %s", self.repository_manager._query_count)
                
                _LOGGER.info("data sucessfully fetched")
                #journeys.journeys[0].journey.departure_date_time = datetime.now()
                return journeys
        except Exception as err:
            _LOGGER.error("Failed to fetch API : %s", err)
            raise UpdateFailed(f"Error fetching api data: {err}")
        
    