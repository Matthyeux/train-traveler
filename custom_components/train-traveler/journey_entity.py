import logging
import pytz

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback


from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)

class JourneyBaseEntity(CoordinatorEntity):


    def __init__(self, coordinator, index, type):
        self.coordinator = coordinator
        self.index = index
        self.type = type
        super().__init__(self.coordinator, context=index)
        
        self.start_label = self.coordinator.data.start.label
        self.end_label = self.coordinator.data.end.label
        self.data = self.coordinator.data.journeys[self.index]
        self.timezone = pytz.timezone("Europe/Paris")

        _LOGGER.debug("Init %s Journey #%s %s - %s", self.type, (self.index + 1), self.start_label, self.end_label)

    @callback
    def _handle_coordinator_update(self) -> None:
        self.data = self.coordinator.data.journeys[self.index]
        self._handle_journey_update()

    
    def _handle_journey_update(self) -> None:
        _LOGGER.warning("You should implement this method")

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": f"{self.coordinator.data.start.name} - {self.coordinator.data.end.name}",
            "sw_version": VERSION,
            "entry_type": None,
        }
    
    def short_start_name(self):
        return self.start_label.replace(" ", "")[0:3].lower()
    
    def short_end_name(self):
        return self.end_label.replace(" ", "")[0:3].lower()
    
    def get_delay(self, disruptions, start_point):
        delay = None
        if len(disruptions) > 0:
            if disruptions[0].severity_effect == "SIGNIFICANT_DELAYS":
                for impacted_objects in disruptions[0].impacted_objects:
                    for impacted_stop in impacted_objects.impacted_stops:
                        if impacted_stop.stop_point.label == start_point:
                            delay = (impacted_stop.ammended_departure_time - impacted_stop.base_departure_time).total_seconds()
        return delay