import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.binary_sensor import (
    BinarySensorEntity
)

from .const import (
    DOMAIN, 
    CONF_NEXT_JOURNEY, 
    CONF_LAST_JOURNEY,
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
    entities = [DisruptionEntity(next_journey_coordinator, index, "next") for index, entity in enumerate(next_journey_coordinator.data.journeys)]
    
    if CONF_LAST_JOURNEY in hass.data[DOMAIN][entry.entry_id]:
        last_journey_coordinator = hass.data[DOMAIN][entry.entry_id][CONF_LAST_JOURNEY]
        entities.extend([DisruptionEntity(last_journey_coordinator, index, "last") for index, entity in enumerate(last_journey_coordinator.data.journeys)])
    
    async_add_entities(entities, True)

class DisruptionEntity(JourneyBaseEntity, BinarySensorEntity):

    def __init__(self, coordinator, index, type):
        super().__init__(coordinator, index, type)

        self._attr_unique_id = f"{self.short_start_name()}_{self.short_end_name()}_{self.type}_journey_disruption_{self.index + 1}"
        self._attr_is_on = self.update_binary_state()

    def _handle_journey_update(self) -> None:
        _LOGGER.debug("[%s] updating: %s - %s", type(self).__name__, self.start_label, self.end_label)

        self._attr_is_on = self.update_binary_state()
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        if self._attr_is_on:
            return {
                ATTR_DISRUPTION_TYPE: self.data.disruptions[0].severity_effect,
                ATTR_DISRUPTION_MESSAGE: self.data.disruptions[0].messages[0]
            }
        return {}
    
    def update_binary_state(self):
        return len(self.data.disruptions) > 0