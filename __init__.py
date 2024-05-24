import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, PLATFORMS, CONF_LAST_JOURNEY, CONF_NEXT_JOURNEY
from .coordinator import JourneyCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    
    _LOGGER.info("Initializing %s integration with platforms: %s and config: %s", DOMAIN, PLATFORMS, entry)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    _LOGGER.info("Add coordinator for next journey")
    next_journey_coordinator = JourneyCoordinator(hass, entry)
    await next_journey_coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id][CONF_NEXT_JOURNEY] = next_journey_coordinator

    if entry.data[CONF_LAST_JOURNEY]:
        _LOGGER.info("Add coordinator for last journey")
        last_journey_coordinator = JourneyCoordinator(hass, entry, last_journey=True)
        await last_journey_coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][entry.entry_id][CONF_LAST_JOURNEY] = last_journey_coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
        hass: HomeAssistant, 
        entry: ConfigEntry
) -> bool:
    
    """Unload a config entry."""
    unload = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload