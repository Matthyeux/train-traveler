from homeassistant.const import Platform

VERSION = "0.1.0"


DOMAIN = "train-traveler"
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

DEFAULT_CONNECTION_URL = "https://api.sncf.com/v1"
DEFAULT_CONNECTION_REGION = "sncf"

DEFAULT_REFRESH_RATE = 720
DEFAULT_JOURNEY_COUNT = 1

CONF_CONNECTION = "connection"
CONF_AREAS = "start_end"
CONF_JOURNEYS_COUNT = "journey"

CONF_FROM = "from"
CONF_TO = "to"
CONF_START_AREA = "start_area"
CONF_END_AREA = "end_area"
CONF_NEXT_JOURNEY = "next_journey"
CONF_LAST_JOURNEY = "last_journey"
CONF_PAUSE_UPDATE_EXPERIMENTAL = "pause_update_experimental"

CONF_AREA_ID = "area_id"
CONF_AREA_NAME = "area_name"
CONF_AREA_LABEL = "area_label"
CONF_AREA_COORD = "area_coord"

ATTR_JOURNEYS_LIST = "journeys"
ATTR_LINE_JOURNEY = "line"
ATTR_DIRECTION_JOURNEY = "direction"
ATTR_DEPARTURE_TIME_JOURNEY = "departure_time"
ATTR_ARRIVAL_TIME_JOURNEY = "arrival_time"
ATTR_DURATION_JOURNEY = "duration"
ATTR_PHYSICAL_MODE_JOURNEY = "physical_mode"
ATTR_DEPARTURE_JOURNEY = "departure"
ATTR_ARRIVAL_JOURNEY = "arrival"
ATTR_DELAY_JOURNEY = "delay"

ATTR_DISRUPTIONS_LIST = "disruptions"
ATTR_DISRUPTION_TYPE = "disruption_type"
ATTR_DISRUPTION_MESSAGE = "disruption_message"
