import logging
import pytz

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.binary_sensor import (
    BinarySensorEntity
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
    entities = [DisruptionEntity(next_journey_coordinator, index, "next") for index, entity in enumerate(next_journey_coordinator.data.journeys)]
    if CONF_LAST_JOURNEY in hass.data[DOMAIN][entry.entry_id]:
        last_journey_coordinator = hass.data[DOMAIN][entry.entry_id][CONF_LAST_JOURNEY]
        entities.extend([DisruptionEntity(last_journey_coordinator, index, "last") for index, entity in enumerate(last_journey_coordinator.data.journeys)])
    
    async_add_entities(entities, True)

class DisruptionEntity(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator, index, type):
        self.coordinator = coordinator
        self.index = index
        super().__init__(self.coordinator, context=index)
        self._attr_is_on

        self._attr_name = f"{type} Journey #{self.index + 1} - disruption".capitalize()
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self.index}_{type}_disruption_sensor"

        if len(self.coordinator.data.journeys[self.index].disruptions) > 0:
            self._attr_is_on = True
        else:
            self._attr_is_on = False

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("Update disruption for journey: %s", self.coordinator.data.start)

        if len(self.coordinator.data.journeys[self.index].disruptions) > 0:
            self._attr_is_on = True
        else:
            self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        if self._attr_is_on:
            return {
                "disruption_type": self.coordinator.data.journeys[self.index].disruptions[0].severity_effect,
                "disruption_message": self.coordinator.data.journeys[self.index].disruptions[0].messages[0]
            }
        return {}
    
    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": f"{self.coordinator.data.start.name} - {self.coordinator.data.end.name}",
            "sw_version": VERSION,
            "entry_type": None,
        }