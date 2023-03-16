
import requests
import random
import time
import logging

logging.basicConfig(level=logging.INFO)

BRIDGE_IP = '172.17.187.253'
AUTHORIZED_USER = 'fAoQajpSocxzpkNodgpZ8u8LCji1epSCYSarbeXq'

GROUP_ACTION_ENDPOINT = f'http://{BRIDGE_IP}/api/{AUTHORIZED_USER}/groups/1/action'
LIGHTSWITCH_STATE_ENDPOINT = f'http://{BRIDGE_IP}/api/{AUTHORIZED_USER}/sensors/2'

color_memory = []
color_memory_names = []

colors_with_hue_levels = (
    {
        'name': 'green',
        'saturation_level': 254,
        'brightness_level': 120,
        'hue_level': 25500,


    },
    {
        'name': 'red',
        'saturation_level': 254,
        'brightness_level': 120,
        'hue_level': 65535,

    },
    {
        'name': 'blue',
        'saturation_level': 254,
        'brightness_level': 120,
        'hue_level': 46920,

    },
    {
        'name': 'yellow',
        'saturation_level': 254,
        'brightness_level': 120,
        'hue_level': 11218,

    },
    {
        'name': 'white',
        'saturation_level': 72,
        'brightness_level': 120,
        'hue_level': 41136,

    }
)


def set_group_state(state: bool, saturation: int, brightness: int, hue: int):
    """Set a new group state, aka change the color of a light group

    Keyword arguments:
    state -- state of the lights in the group (True or False)
    saturation -- saturation value (int)
    brightness -- brightness value (int)
    hue -- hue value (int)

    Hue Docs:
    https://developers.meethue.com/develop/hue-api/groupds-api/#set-gr-state

    Returns:
    JSON response that details the success of sending each state parameter to the group.
    """

    r = requests.put(
        url=GROUP_ACTION_ENDPOINT,
        json={
            'on': state,
            'sat': saturation,
            'bri': brightness,
            'hue': hue
        }
    )

    return r.json()


def get_switch_state():
    """Get the current state of the lightswitch

    Keyword arguments:
    /

    Hue Docs:
    https://developers.meethue.com/develop/hue-api/5-sensors-api/#get-sensor

    Returns:
    JSON response that details the state of the lightswitch
    """

    r = requests.get(
        url=LIGHTSWITCH_STATE_ENDPOINT
    )

    return r.json()['state']


def game_over():
    """Turn off all lights in group

    Keyword arguments:
    /

    Returns:
    /
    """

    set_group_state(
        state=False,
        saturation=0,
        brightness=0,
        hue=0
    )

    return


def main():
    """Game Loop:

        1) picks a random color from the color tuple
        2) adds the color to color memory
        3) displays the color memory on a light group, each color is followed up by white
        4) waits for user input
        5) compares color memory to user input list
        6) runs game over method if both lists don't match

    Keyword arguments:
    /

    Hue Docs:
    /

    Returns:
    /
    """

    while True:

        new_color = colors_with_hue_levels[random.randint(0, 3)]

        color_memory.append(new_color)
        color_memory_names.append(new_color['name'])

        for item in color_memory:

            set_group_state(
                state=True,
                saturation=item['saturation_level'],
                brightness=item['brightness_level'],
                hue=item['hue_level']
            )

            time.sleep(2)

            set_group_state(
                state=True,
                saturation=colors_with_hue_levels[4]['saturation_level'],
                brightness=colors_with_hue_levels[4]['brightness_level'],
                hue=colors_with_hue_levels[4]['hue_level']
            )

        user_inputs = []

        while len(user_inputs) < len(color_memory):

            previous_timestamp = get_switch_state()['lastupdated']
            timestamp = previous_timestamp

            while previous_timestamp == timestamp:

                state = get_switch_state()

                if (previous_timestamp != state['lastupdated']):

                    buttonevent = state['buttonevent']
                    timestamp = state['lastupdated']

            match buttonevent:
                case 1000 | 1001 | 1002 | 1003:
                    input = 'yellow'
                case 2000 | 2001 | 2002 | 2003:
                    input = 'green'
                case 3000 | 3001 | 3002 | 3003:
                    input = 'blue'
                case 4000 | 4001 | 4002 | 4003:
                    input = 'red'

            user_inputs.append(input)

        if color_memory_names != user_inputs:
            break

    game_over()


if __name__ == "__main__":
    main()
