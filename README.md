# Train Traveler

Train Traveler is a custom component for Home Assistant that retrieves the next train schedules for a given route as well as the last train of the day and disruptions if exists.

## Features

- Display the next train schedules for a specific route.
- Display the schedule of the last train of the day.
- Display the dirsuption for the next journey if exists

## Installation

### Prerequisites

- Home Assistant installed and configured.
- An account with access to the [SNCF Portal](https://numerique.sncf.com/startup/api/token-developpeur/)..

### Manual Installation

1. **Download the component files:**

    Clone this repository or download the files and place them in the `custom_components/train_traveler` directory of your Home Assistant configuration.

    ```bash
    git clone https://github.com/Matthyeux/train_traveler.git
    
    cp -r train_traveler/custom_components/* custom_components/train_traveler/
    ```

2. **Restart Home Assistant:**

    Restart Home Assistant for the changes to take effect.

    You can restart Home Assistant from the user interface under `Configuration > Server Controls > Restart`.

## Configuration via the User Interface

1. **Add the component via the UI:**

    Go to `Configuration > Integrations` and click the `+ Add Integration` button. Search for `Train Traveler` and follow the on-screen instructions to add the configuration.

2. **Configure the parameters:**

    - **Page 1:**
        - **API URL:** Enter the train schedule API URL. (default: https://api.sncf.com/v1)
        - **Region:** Select your region. (default: sncf)
        - **API Key:** Enter your API key.
    - **Page 2:**
        - **Departure Point:** Select the departure station.
        - **Arrival Point:** Select the arrival station.
    - **Page 3:**
        - **Validate Departure station**
        - **Validate Arrival station**
    - **Page 4:**
        - **Counter:** Set a counter for the number of next train schedules to retrieve. (default: 1)
        - **Refresh rate:** refresh rate to update entities (default: 740 seconds)
        - **Last journey:** Enable or no the last journey for your line

## Usage

Once configured, the Train Traveler component will create sensors in Home Assistant for the next train schedules and the last train of the day. You can use them in your dashboards or automations.

### Next Journey Entity - Sensor

| Attribute       | Description                                 | Example Value         |
|-----------------|---------------------------------------------|-----------------------|
| `state`         | The date and time of the next train         | `2024-05-18T15:30:00` |
| `line`          | The train line                              | `RER B`               |
| `departure`     | The departure station                       | `Gare du Nord`        |
| `arrival`       | The arrival station                         | `Charles de Gaulle`   |
| `arrival_time`  | The date and time of arrival                | `2024-05-18T16:00:00` |
| `direction`     | The final destination of the train (terminus)| `Charles de Gaulle`   |
| `duration`         | The duration of the journey in seconds       | `1800` |
| `physical_mode` | The mode of transport                       | `TER / Intercité`               |

### Next Journey Departure Date Time Entity - Sensor

| Attribute       | Description                                 | Example Value         |
|-----------------|---------------------------------------------|-----------------------|
| `state`         | The date and time of the next train         | `2024-05-18T15:30:00` |

### Next Journey Arrival Date Time Entity - Sensor

| Attribute       | Description                                 | Example Value         |
|-----------------|---------------------------------------------|-----------------------|
| `state`         | The date and time of arrival         | `2024-05-18T16:00:00` |

### Next Journey Duration Entity - Sensor

| Attribute       | Description                                 | Example Value         |
|-----------------|---------------------------------------------|-----------------------|
| `state`         | The duration of the journey in seconds       | `1800` |

### Next Journey Disruption - Binary Sensor

| Attribute       | Description                                 | Example Value         |
|-----------------|---------------------------------------------|-----------------------|
| `state`         | The duration of the journey in seconds       | `on\|off` |
| `type`         | The type of disruption      | `SIGNIFICANT_DELAYS\|REDUCED_SERVICE\|MODIFIED_SERVICE\|ADDITIONAL_SERVICE` |
| `message`         | The message of the disruption       | `on\|off` |

### Next Journey Delay - Sensor
| Attribute       | Description                                 | Example Value         |
|-----------------|---------------------------------------------|-----------------------|
| `state`         | The time of delay for the current disruption if exists in seconds      | `300` |



### Example Lovelace Card

Add a custom card to your Lovelace dashboard to display the train schedules:

```yaml
type: vertical-stack
cards:
  - type: entity
    entity: sensor.next_journey_1
    name: Next Journey
  - type: entities
    entities:
      - type: attribute
        entity: sensor.next_journey_1
        name: Line
        icon: mdi:train
        attribute: line
      - type: attribute
        entity: sensor.next_journey_1
        name: Direction
        icon: mdi:directions
        attribute: direction
      - entity: sensor.next_journey_1_departure_date_time
        name: Departure Time
        icon: mdi:clock-fast
      - entity: sensor.next_journey_1_arrival_date_time
        name: Arrival Time
        icon: mdi:ray-end
      - entity: sensor.next_journey_1_duration
        name: Duration
        unit: seconds
        icon: mdi:timeline-clock-outline
      - type: attribute
        entity: sensor.next_journey_1
        name: Type
        icon: mdi:information-box-outline
        attribute: physical_mode
  - type: conditional
    conditions:
      - condition: state
        entity: binary_sensor.next_journey_1_disruption
        state: 'on'
    card:
      type: entities
      entities:
        - entity: sensor.next_journey_1_delay
          name: Delay
          icon: mdi:clock-start
        - entity: binary_sensor.next_journey_1_disruption
          type: attribute
          name: Message
          icon: mdi:alert-circle
          attribute: disruption_message
  - type: entity
    entity: sensor.last_journey_1
    name: Last Journey
title: Departure - Arrival

```

## Development

If you want to contribute to the development of this component, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/Matthyeux/train_traveler.git
```

2. Create a branch for your changes:

```bash
git checkout -b feature/add-feature
```

3. Make your changes and push the branch:

```bash
git push origin feature/add-feature
```

4. Open a Pull Request on GitHub.

## Support

For any questions or issues, please open an issue on GitHub.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.