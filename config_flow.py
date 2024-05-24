
import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL, CONF_URL, CONF_REGION
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector

from sncf.connections.connection_manager import ApiConnectionManager
from sncf.repositories.place_repository import ApiPlaceRepository
from sncf.repositories.repository_manager import ApiRepository
from sncf.services.info_service import InfoService


from .const import (
    DOMAIN, 
    DEFAULT_CONNECTION_URL, DEFAULT_CONNECTION_REGION, DEFAULT_REFRESH_RATE, DEFAULT_JOURNEY_COUNT,
    CONF_CONNECTION, CONF_LAST_JOURNEY, CONF_FROM, CONF_TO, CONF_START_AREA, CONF_END_AREA,
    CONF_AREAS, CONF_JOURNEYS_COUNT, CONF_AREA_NAME, CONF_AREA_COORD, CONF_AREA_ID, CONF_AREA_LABEL
)

CONNECTION_SCHEMA = vol.Schema({
    vol.Required(CONF_URL, default=DEFAULT_CONNECTION_URL): cv.string,
    vol.Required(CONF_REGION, default=DEFAULT_CONNECTION_REGION): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
})


AREA_SCHEMA = vol.Schema({
    vol.Required(CONF_FROM): cv.string,
    vol.Required(CONF_TO): cv.string
})

JOURNEY_SCHEMA = vol.Schema({
    vol.Required(CONF_JOURNEYS_COUNT, default=DEFAULT_JOURNEY_COUNT): cv.positive_int,
    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_REFRESH_RATE): cv.positive_int,
    vol.Optional(CONF_LAST_JOURNEY): cv.boolean
})


async def validate_auth(connection: ApiConnectionManager, hass: core.HomeAssistant):
    infoService: InfoService = InfoService(ApiRepository(connection=connection))
    auth = await hass.async_add_executor_job(infoService.validate_coverage_auth)
    if not auth:
        raise ValueError
    return True    

async def fetch_area(place: str, connection, hass: core.HomeAssistant):
    place_repository = ApiPlaceRepository(connection=connection)
    try:
        areas = await hass.async_add_executor_job(place_repository.find_areas_from_places, place)
    except Exception:
        raise ValueError

    return areas

class TrainTravelerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for sncf-integration."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        errors = {}

        if user_input is not None:
            try:
                connection = ApiConnectionManager(user_input[CONF_URL], user_input[CONF_API_KEY], user_input[CONF_REGION])
                await validate_auth(connection, self.hass)
            except ValueError:
                errors["base"] = "auth_error"
            if not errors:
                self.data = user_input
                self.data[CONF_CONNECTION] = {
                    CONF_URL: user_input[CONF_URL],
                    CONF_API_KEY: user_input[CONF_API_KEY],
                    CONF_REGION: user_input[CONF_REGION]
                }
                self.data[CONF_AREAS] = {}
                return await self.async_step_start_end()
        
        return self.async_show_form(
            step_id="user", data_schema=CONNECTION_SCHEMA, errors=errors
        )
    
    async def async_step_start_end(self, user_input=None):
        """Handle the start/end points step."""
        errors = {}

        if user_input is not None:
            try:
                connection = ApiConnectionManager(self.data[CONF_CONNECTION][CONF_URL], self.data[CONF_CONNECTION][CONF_API_KEY], self.data[CONF_CONNECTION][CONF_REGION])
                start = await fetch_area(user_input[CONF_FROM], connection, self.hass)
                end = await fetch_area(user_input[CONF_TO], connection, self.hass)
            except ValueError:
                errors["base"] = "fetch_area_error"

            if not errors:
                self.data[CONF_AREAS] = {
                    "from_area": start,
                    "to_area": end
                }
            return await self.async_step_validate_start_end()


        return self.async_show_form(
            step_id="start_end",
            data_schema=AREA_SCHEMA,
            errors=errors,
        )
    
    async def async_step_validate_start_end(self, user_input=None):
        """Handle validation of the start/end points step."""
        errors = {}

        if user_input is not None:
            start = next((area for area in self.data[CONF_AREAS]["from_area"] if area.name == user_input[CONF_START_AREA]), None)
            end = next((area for area in self.data[CONF_AREAS]["to_area"] if area.name == user_input[CONF_END_AREA]), None)
            self.data[CONF_START_AREA] = {
                CONF_AREA_ID: start.stop_area.id,
                CONF_AREA_NAME: start.stop_area.name,
                CONF_AREA_LABEL: start.stop_area.label,
                CONF_AREA_COORD: {
                    "lon": start.stop_area.coord["lon"],
                    "lat": start.stop_area.coord["lat"]
                }
            }
            
            self.data[CONF_END_AREA] = {
                CONF_AREA_ID: end.stop_area.id,
                CONF_AREA_NAME: end.stop_area.name,
                CONF_AREA_LABEL: end.stop_area.label,
                CONF_AREA_COORD: {
                    "lon": end.stop_area.coord["lon"],
                    "lat": end.stop_area.coord["lat"]
                }
            }
            del self.data[CONF_AREAS]
            return await self.async_step_journey()
        
        data_schema = vol.Schema(
            {
                vol.Required(CONF_START_AREA, default=self.data[CONF_AREAS]["from_area"][0].name): selector.SelectSelector(
                     selector.SelectSelectorConfig(
                         options=[area.name for area in self.data[CONF_AREAS]["from_area"]], mode=selector.SelectSelectorMode.DROPDOWN
                         )),
                vol.Required(CONF_END_AREA, default=self.data[CONF_AREAS]["to_area"][0].name): selector.SelectSelector(
                     selector.SelectSelectorConfig(
                         options=[area.name for area in self.data[CONF_AREAS]["to_area"]], mode=selector.SelectSelectorMode.DROPDOWN
                         ))
            }
        )

        return self.async_show_form(
            step_id="validate_start_end",
            data_schema=data_schema,
            errors=errors
        )
    

    async def async_step_journey(self, user_input=None):
        """Handle the journey step."""
        errors = {}

        if user_input is not None:
            # Finalize the configuration and create the entry
            self.data[CONF_JOURNEYS_COUNT] = user_input[CONF_JOURNEYS_COUNT]
            self.data[CONF_SCAN_INTERVAL] = user_input[CONF_SCAN_INTERVAL]
            self.data[CONF_LAST_JOURNEY] = user_input[CONF_LAST_JOURNEY] if CONF_LAST_JOURNEY in user_input else False

            return self.async_create_entry(title=f"{self.data[CONF_START_AREA][CONF_AREA_LABEL]} - {self.data[CONF_END_AREA][CONF_AREA_LABEL]}" , data=self.data)


        return self.async_show_form(
            step_id="journey",
            data_schema=JOURNEY_SCHEMA,
            errors=errors,
        )
