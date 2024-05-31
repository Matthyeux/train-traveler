import logging

from datetime import datetime

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass
)

from .const import (
    DOMAIN, 
    CONF_NEXT_JOURNEY, 
    CONF_LAST_JOURNEY,
    ATTR_JOURNEYS_LIST, 
    ATTR_LINE_JOURNEY, 
    ATTR_DIRECTION_JOURNEY, 
    ATTR_DEPARTURE_JOURNEY, 
    ATTR_ARRIVAL_JOURNEY, 
    ATTR_DEPARTURE_TIME_JOURNEY, 
    ATTR_ARRIVAL_TIME_JOURNEY, 
    ATTR_DURATION_JOURNEY, 
    ATTR_PHYSICAL_MODE_JOURNEY, 
    ATTR_DELAY_JOURNEY,
    ATTR_DISRUPTIONS_LIST,
    ATTR_DISRUPTION_TYPE,
    ATTR_DISRUPTION_MESSAGE
)
from .journey_entity import JourneyBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
):

    _LOGGER.debug("Calling async_setup_entry entry=%s", entry)

    next_journey_coordinator = hass.data[DOMAIN][entry.entry_id][CONF_NEXT_JOURNEY]
    entities = [entity(next_journey_coordinator, index, "next") for index, ent in enumerate(next_journey_coordinator.data.journeys) for entity in (NextJourneyEntity, DepartureEntity, ArrivalEntity, DurationEntity, DelayEntity)]
    entities.extend([JourneyEntity(next_journey_coordinator, 0, "next")])

    if CONF_LAST_JOURNEY in hass.data[DOMAIN][entry.entry_id]:
        last_journey_coordinator = hass.data[DOMAIN][entry.entry_id][CONF_LAST_JOURNEY]
        entities.extend([entity(last_journey_coordinator, index, "last") for index, ent in enumerate(last_journey_coordinator.data.journeys) for entity in (NextJourneyEntity, DepartureEntity, ArrivalEntity, DurationEntity, DelayEntity)])

    async_add_entities(entities, True)



class NextJourneyEntity(JourneyBaseEntity, SensorEntity):
    def __init__(self, coordinator, index, type):
        super().__init__(coordinator, index, type)

        self._attr_unique_id = f"{self.short_start_name()}_{self.short_end_name()}_{self.type}_journey_{self.index + 1}"
        self._attr_native_value = self.timezone.localize(self.data.journey.departure_date_time)

    def _handle_journey_update(self) -> None:
        _LOGGER.debug("[%s] updating: %s - %s", type(self).__name__, self.start_label, self.end_label)
        self._attr_native_value = self.timezone.localize(self.data.journey.departure_date_time)
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.TIMESTAMP
    
    @property
    def extra_state_attributes(self):
        return {
            ATTR_LINE_JOURNEY: self.data.journey.sections[0].informations.label,
            ATTR_DIRECTION_JOURNEY: self.data.journey.sections[0].informations.direction,
            ATTR_DEPARTURE_TIME_JOURNEY: self.timezone.localize(self.data.journey.departure_date_time),
            ATTR_ARRIVAL_TIME_JOURNEY: self.timezone.localize(self.data.journey.arrival_date_time),
            ATTR_DURATION_JOURNEY: self.data.journey.sections[0].duration,
            ATTR_PHYSICAL_MODE_JOURNEY: self.data.journey.sections[0].informations.physical_mode,
            ATTR_DEPARTURE_JOURNEY: self.start_label,
            ATTR_ARRIVAL_JOURNEY: self.end_label
        }
    

class JourneyEntity(JourneyBaseEntity, SensorEntity):
    def __init__(self, coordinator, index, type):
        super().__init__(coordinator, index, type)
        self._attr_unique_id = f"{self.short_start_name()}_{self.short_end_name()}_journeys"
        self._attr_native_value = self.timezone.localize(self.data.journey.departure_date_time)

    def _handle_journey_update(self) -> None:
        _LOGGER.debug("[%s] updating: %s - %s", type(self).__name__, self.start_label, self.end_label)
        self._attr_native_value = self.timezone.localize(self.data.journey.departure_date_time)
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.TIMESTAMP

    @property
    def extra_state_attributes(self):
        journeys = []
        for data in self.coordinator.data.journeys:
            
            disruptions = []
            for disruption in data.disruptions:
                disruptions.append({
                    ATTR_DISRUPTION_TYPE: disruption.severity_effect,
                    ATTR_DISRUPTION_MESSAGE: disruption.messages[0],
                    
                }) 
            journeys.append({
                ATTR_LINE_JOURNEY: data.journey.sections[0].informations.label,
                ATTR_DIRECTION_JOURNEY: data.journey.sections[0].informations.direction,
                ATTR_DEPARTURE_TIME_JOURNEY: self.timezone.localize(data.journey.departure_date_time),
                ATTR_ARRIVAL_TIME_JOURNEY: self.timezone.localize(data.journey.arrival_date_time),
                ATTR_DURATION_JOURNEY: data.journey.sections[0].duration,
                ATTR_PHYSICAL_MODE_JOURNEY: data.journey.sections[0].informations.physical_mode,
                ATTR_DEPARTURE_JOURNEY: self.start_label,
                ATTR_ARRIVAL_JOURNEY: self.end_label,
                ATTR_DISRUPTIONS_LIST: disruptions,
                ATTR_DELAY_JOURNEY: self.get_delay(data.disruptions, self.start_label)
            })

        return {
            ATTR_JOURNEYS_LIST: journeys
        }
    

class DepartureEntity(JourneyBaseEntity, SensorEntity):

    def __init__(self, coordinator, index, type):
        super().__init__(coordinator, index, type)

        self._attr_unique_id = f"{self.short_start_name()}_{self.short_end_name()}_{self.type}_journey_departure_{self.index + 1}"
        self._attr_native_value = self.timezone.localize(self.data.journey.departure_date_time)

    def _handle_journey_update(self) -> None:
        _LOGGER.debug("[%s] updating: %s - %s", type(self).__name__, self.start_label, self.end_label)
        self._attr_native_value = self.timezone.localize(self.data.journey.departure_date_time)
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.TIMESTAMP
    


class ArrivalEntity(JourneyBaseEntity, SensorEntity):
    def __init__(self, coordinator, index, type):
        super().__init__(coordinator, index, type)

        self._attr_unique_id = f"{self.short_start_name()}_{self.short_end_name()}_{self.type}_journey_arrival_{self.index + 1}"
        self._attr_native_value = self.timezone.localize(self.data.journey.arrival_date_time)

    def  _handle_journey_update(self) -> None:
        _LOGGER.debug("[%s] updating: %s - %s", type(self).__name__, self.start_label, self.end_label)
        self._attr_native_value = self.timezone.localize(self.data.journey.arrival_date_time)
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.TIMESTAMP
    
    
class DurationEntity(JourneyBaseEntity, SensorEntity):
    def __init__(self, coordinator, index, type):
        super().__init__(coordinator, index, type)

        self._attr_native_unit_of_measurement = "s"
        self._attr_unique_id = f"{self.short_start_name()}_{self.short_end_name()}_{self.type}_journey_duration_{self.index + 1}"
        self._attr_native_value = self.data.journey.sections[0].duration

    def _handle_journey_update(self) -> None:
        _LOGGER.debug("[%s] updating: %s - %s", type(self).__name__, self.start_label, self.end_label)
        self._attr_native_value = self.data.journey.sections[0].duration
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.DURATION
    
    @property
    def state_class(self) -> SensorStateClass:
        return SensorStateClass.MEASUREMENT
    

class DelayEntity(JourneyBaseEntity, SensorEntity):
    def __init__(self, coordinator, index, type):
        super().__init__(coordinator, index, type)


        self._attr_native_unit_of_measurement = "s"
        self._attr_unique_id = f"{self.short_start_name()}_{self.short_end_name()}_{self.type}_journey_disruption_delay_{self.index + 1}"
        self._attr_native_value = self.get_delay(self.data.disruptions, self.start_label)

    def _handle_journey_update(self) -> None:
        _LOGGER.debug("[%s] updating: %s - %s", type(self).__name__, self.start_label, self.end_label)
        self._attr_native_value = self.get_delay(self.data.disruptions, self.start_label)
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.DURATION
    
    @property
    def state_class(self) -> SensorStateClass:
        return SensorStateClass.MEASUREMENT
    
