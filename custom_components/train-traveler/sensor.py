import logging
import pytz

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass
)

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, VERSION, CONF_NEXT_JOURNEY, CONF_LAST_JOURNEY

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
):

    _LOGGER.debug("Calling async_setup_entry entry=%s", entry)

    next_journey_coordinator = hass.data[DOMAIN][entry.entry_id][CONF_NEXT_JOURNEY]
    entities = [entity(next_journey_coordinator, index, "next") for index, ent in enumerate(next_journey_coordinator.data.journeys) for entity in (JourneyEntity, DepartureEntity, ArrivalEntity, DurationEntity, DelayEntity)]
    
    if CONF_LAST_JOURNEY in hass.data[DOMAIN][entry.entry_id]:
        last_journey_coordinator = hass.data[DOMAIN][entry.entry_id][CONF_LAST_JOURNEY]
        entities.extend([entity(last_journey_coordinator, index, "last") for index, ent in enumerate(last_journey_coordinator.data.journeys) for entity in (JourneyEntity, DepartureEntity, ArrivalEntity, DurationEntity, DelayEntity)])

    async_add_entities(entities, True)


class JourneyEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, index, type):
        self.coordinator = coordinator
        super().__init__(self.coordinator, context=index)
        self.index = index

        self._attr_name = f"{type} Journey #{self.index +1 }".capitalize()
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self.index}_{type}_journey_sensor"
        self._attr_native_value = pytz.timezone('Europe/Paris').localize(self.coordinator.data.journeys[self.index].journey.departure_date_time)

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("Update journey: %s", self.coordinator.data.start)
        self._attr_native_value = pytz.timezone('Europe/Paris').localize(self.coordinator.data.journeys[self.index].journey.departure_date_time)
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.TIMESTAMP
    
    @property
    def extra_state_attributes(self):
        return {
            "line": self.coordinator.data.journeys[self.index].journey.sections[0].informations.label,
            "direction": self.coordinator.data.journeys[self.index].journey.sections[0].informations.direction,
            "arrival_time": pytz.timezone('Europe/Paris').localize(self.coordinator.data.journeys[self.index].journey.arrival_date_time),
            "physical_mode": self.coordinator.data.journeys[self.index].journey.sections[0].informations.physical_mode,
            "departure": self.coordinator.data.start.label,
            "arrival": self.coordinator.data.end.label
        }
    
    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": f"{self.coordinator.data.start.name} - {self.coordinator.data.end.name}",
            "sw_version": VERSION,
            "entry_type": None,
        }

class DepartureEntity(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, index, type):
        self.coordinator = coordinator
        super().__init__(self.coordinator, context=index)
        self.index = index

        self._attr_name = f"{type} Journey #{self.index + 1} - Departure Date Time".capitalize()
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self.index}_{type}_departure_sensor"
        self._attr_native_value = pytz.timezone('Europe/Paris').localize(self.coordinator.data.journeys[self.index].journey.departure_date_time)

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("Update departure journey: %s", self.coordinator.data.start)
        self._attr_native_value = pytz.timezone('Europe/Paris').localize(self.coordinator.data.journeys[self.index].journey.departure_date_time)
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.TIMESTAMP
    
    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": f"{self.coordinator.data.start.name} - {self.coordinator.data.end.name}",
            "sw_version": VERSION,
            "entry_type": None,
        }


class ArrivalEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, index, type):
        self.coordinator = coordinator
        super().__init__(self.coordinator, context=index)
        self.index = index 

        self._attr_name = f"{type} Journey #{self.index + 1} - Arrival Date Time".capitalize()
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self.index}_{type}_arrival_sensor"
        self._attr_native_value = pytz.timezone('Europe/Paris').localize(self.coordinator.data.journeys[self.index].journey.arrival_date_time)

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("Update arrival journey: %s", self.coordinator.data.start)
        self._attr_native_value = pytz.timezone('Europe/Paris').localize(self.coordinator.data.journeys[self.index].journey.arrival_date_time)
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.TIMESTAMP
    
    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": f"{self.coordinator.data.start.name} - {self.coordinator.data.end.name}",
            "sw_version": VERSION,
            "entry_type": None,
        }
    
class DurationEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, index, type):
        self.coordinator = coordinator
        super().__init__(self.coordinator, context=index)
        self.index = index 

        self._attr_name = f"{type} Journey #{self.index + 1} - Duration".capitalize()
        self._attr_native_unit_of_measurement = "s"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self.index}_{type}_duration_sensor"
        self._attr_native_value = self.coordinator.data.journeys[self.index].journey.sections[0].duration

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("Update arrival journey: %s", self.coordinator.data.start)
        self._attr_native_value = self.coordinator.data.journeys[self.index].journey.sections[0].duration
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.DURATION
    
    @property
    def state_class(self) -> SensorStateClass:
        return SensorStateClass.MEASUREMENT
    
    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": f"{self.coordinator.data.start.name} - {self.coordinator.data.end.name}",
            "sw_version": VERSION,
            "entry_type": None,
        }


class DelayEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, index, type):
        self.coordinator = coordinator
        super().__init__(self.coordinator, context=index)
        self.index = index

        self._attr_name = f"{type} Journey #{self.index + 1} - Delay".capitalize()
        self._attr_native_unit_of_measurement = "s"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self.index}_{type}_disruption_message_sensor"
        self._attr_native_value = self.get_delay(self.coordinator.data.journeys[self.index].disruptions, self.coordinator.data.start)

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("Update delay journey: %s", self.coordinator.data.start)
        self._attr_native_value = self.get_delay(self.coordinator.data.journeys[self.index].disruptions, self.coordinator.data.start)
        self.async_write_ha_state()

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.DURATION
    
    @property
    def state_class(self) -> SensorStateClass:
        return SensorStateClass.MEASUREMENT

    
    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": f"{self.coordinator.data.start.name} - {self.coordinator.data.end.name}",
            "sw_version": VERSION,
            "entry_type": None,
        }

    def get_delay(self, disruptions, start_point):
        delay = None
        if len(disruptions) > 0:
            if disruptions[0].severity_effect == "SIGNIFICANT_DELAYS":
                for impacted_objects in disruptions[0].impacted_objects:
                    for impacted_stop in impacted_objects.impacted_stops:
                        if impacted_stop.stop_point.name == start_point.name:
                            delay = (impacted_stop.ammended_departure_time - impacted_stop.base_departure_time).total_seconds()
        return delay
    
