from homeassistant.const import Platform

VERSION = "0.1.0"


DOMAIN = "sncf-integration"
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

DEFAULT_CONNECTION_URL = "https://api.sncf.com/v1"
DEFAULT_CONNECTION_REGION = "sncf"

DEFAULT_REFRESH_RATE = 540
DEFAULT_JOURNEY_COUNT = 2

CONF_CONNECTION = "connection"
CONF_AREAS = "start_end"
CONF_JOURNEYS_COUNT = "journey"

CONF_FROM = "from"
CONF_TO = "to"
CONF_START_AREA = "start_area"
CONF_END_AREA = "end_area"
CONF_NEXT_JOURNEY = "next_journey"
CONF_LAST_JOURNEY = "last_journey"

CONF_AREA_ID = "area_id"
CONF_AREA_NAME = "area_name"
CONF_AREA_LABEL = "area_label"
CONF_AREA_COORD = "area_coord"