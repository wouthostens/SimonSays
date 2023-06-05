
import requests
import random
import logging
import asyncio

from homeassistant.const import EVENT_CALL_SERVICE

logging.basicConfig(level=logging.INFO)

BRIDGE_IP = '172.17.187.253'
AUTHORIZED_USER = 'fAoQajpSocxzpkNodgpZ8u8LCji1epSCYSarbeXq'

GROUP_ACTION_ENDPOINT = f'http://{BRIDGE_IP}/api/{AUTHORIZED_USER}/groups/1/action'
LIGHTSWITCH_STATE_ENDPOINT = f'http://{BRIDGE_IP}/api/{AUTHORIZED_USER}/sensors/2'


colors_with_hue_levels = (
    {
        'name': 'green',
        'translation': 'groen',
        'saturation_level': 254,
        'brightness_level': 120,
        'hue_level': 25500,
        'rgb_percentage_red': 0,
        'rgb_percentage_green': 100,
        'rgb_percentage_blue': 0,


    },
    {
        'name': 'red',
        'translation': 'rood',
        'saturation_level': 254,
        'brightness_level': 120,
        'hue_level': 65535,
        'rgb_percentage_red': 100,
        'rgb_percentage_green': 0,
        'rgb_percentage_blue': 0,

    },
    {
        'name': 'blue',
        'translation': 'blauw',
        'saturation_level': 254,
        'brightness_level': 120,
        'hue_level': 46920,
        'rgb_percentage_red': 0,
        'rgb_percentage_green': 0,
        'rgb_percentage_blue': 100,

    },
    {
        'name': 'yellow',
        'translation': 'geel',
        'saturation_level': 254,
        'brightness_level': 120,
        'hue_level': 11218,
        'rgb_percentage_red': 100,
        'rgb_percentage_green': 90,
        'rgb_percentage_blue': 0,

    },
    {
        'name': 'white',
        'translation': 'wit',
        'saturation_level': 72,
        'brightness_level': 120,
        'hue_level': 41136,
        'rgb_percentage_red': 100,
        'rgb_percentage_green': 100,
        'rgb_percentage_blue': 100,

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

    r = task.executor(requests.put,
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

    r = task.executor(requests.get,
                      url=LIGHTSWITCH_STATE_ENDPOINT
                      )

    return r.json()['state']

def update_score_board(name, score):

    scoreboard = input_text.simon_says_scoreboard

    if scoreboard != "":

        scoreboard_list = scoreboard.splitlines()
        
        custom_list = [ item.split(": ")[0] for item in scoreboard_list ]
        
        if name in custom_list:
            
            index = custom_list.index(name)
            old_score = int(scoreboard_list[index].split(": ")[1])

            if score > old_score:

                scoreboard_list[index] = f"{name}: {score}"

        else:
            scoreboard_list.append(f"{name}: {score}")
        
        final_list = sorted(scoreboard_list, key=lambda x: int(x.split(": ")[1]), reverse=True)

        service.call(domain="input_text", name="set_value", value='\n'.join(final_list), entity_id="input_text.simon_says_scoreboard")
    
    else:

        service.call(domain="input_text", name="set_value", value=f"{name}: {score}", entity_id="input_text.simon_says_scoreboard")

    



@service
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

    service.call(domain="switch", name="turn_off", entity_id="switch.mosfet_blauw")
    service.call(domain="switch", name="turn_off", entity_id="switch.mosfet_rood")
    service.call(domain="switch", name="turn_off", entity_id="switch.mosfet_groen")
    
    service.call(domain="input_text", name="set_value",
                 value=f"GAME OVER!", entity_id="input_text.simon_says_algemeen")
    
    asyncio.sleep(0.5)

    service.call(domain="input_text", name="set_value", value="/",
                 entity_id="input_text.simon_says_kleur")
    
    service.call(domain="input_text", name="set_value",
                         value=random.randint(0, 10000), entity_id="input_text.fastled_led_start")
    
    for index in range(0, 149):
        
        if input_text.simon_says_algemeen != "GAME OVER!":
            break

        item = random.choice(colors_with_hue_levels)

        service.call(domain="input_number", name="set_value", value=index, entity_id="input_number.fastled_led_number")
        service.call(domain="input_text", name="set_value", value=item['rgb_percentage_red'], entity_id="input_text.fastled_led_color_red")
        service.call(domain="input_text", name="set_value", value=item['rgb_percentage_green'], entity_id="input_text.fastled_led_color_green")
        service.call(domain="input_text", name="set_value", value=item['rgb_percentage_blue'], entity_id="input_text.fastled_led_color_blue")
        service.call(domain="input_text", name="set_value", value=index, entity_id="input_text.fastled_status")

        asyncio.sleep(0.5)
    
    
@service
def simon_says():
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
    
    color_memory = []
    color_memory_names = []
    score = 0

    service.call(domain="input_number", name="set_value",
                 value=score, entity_id="input_number.simon_says_score")
    
    service.call(domain="input_text", name="set_value",
                         value=random.randint(0, 10000), entity_id="input_text.fastled_led_start")

    while True:

        new_color = colors_with_hue_levels[random.randint(0, 3)]

        color_memory.append(new_color)
        color_memory_names.append(new_color['name'])

        for index, item in enumerate(color_memory):

            service.call(domain="input_text", name="set_value",
                         value=item['translation'], entity_id="input_text.simon_says_kleur")
            
            service.call(domain="switch", name="turn_off", entity_id="switch.mosfet_blauw")
            service.call(domain="switch", name="turn_off", entity_id="switch.mosfet_rood")
            service.call(domain="switch", name="turn_off", entity_id="switch.mosfet_groen")
            
            if item['name'] == 'blue': 
                
                service.call(domain="switch", name="turn_on", entity_id="switch.mosfet_blauw")
            
            elif item['name'] == 'green':

                service.call(domain="switch", name="turn_on", entity_id="switch.mosfet_groen")
            
            elif item['name'] == 'red':

                service.call(domain="switch", name="turn_on", entity_id="switch.mosfet_rood")
            
            elif item['name'] == 'yellow':
                service.call(domain="switch", name="turn_on", entity_id="switch.mosfet_rood")
                service.call(domain="switch", name="turn_on", entity_id="switch.mosfet_groen")
            
            service.call(domain="input_number", name="set_value", value=index, entity_id="input_number.fastled_led_number")
            service.call(domain="input_text", name="set_value", value=item['rgb_percentage_red'], entity_id="input_text.fastled_led_color_red")
            service.call(domain="input_text", name="set_value", value=item['rgb_percentage_green'], entity_id="input_text.fastled_led_color_green")
            service.call(domain="input_text", name="set_value", value=item['rgb_percentage_blue'], entity_id="input_text.fastled_led_color_blue")
            service.call(domain="input_text", name="set_value", value=index, entity_id="input_text.fastled_status")

            previous_color = color_memory[index -
                                          1]['translation'] if len(color_memory) > 1 else '/'
            current_color = item['translation']
            service.call(domain="input_text", name="set_value",
                         value=f"VORIG: {previous_color}\nHUIDIG: {current_color}", entity_id="input_text.simon_says_algemeen")

            set_group_state(
                state=True,
                saturation=item['saturation_level'],
                brightness=item['brightness_level'],
                hue=item['hue_level']
            )

            asyncio.sleep(3)

        set_group_state(
            state=True,
            saturation=colors_with_hue_levels[4]['saturation_level'],
            brightness=colors_with_hue_levels[4]['brightness_level'],
            hue=colors_with_hue_levels[4]['hue_level']
        )

        service.call(domain="switch", name="turn_on", entity_id="switch.mosfet_blauw")
        service.call(domain="switch", name="turn_on", entity_id="switch.mosfet_rood")
        service.call(domain="switch", name="turn_on", entity_id="switch.mosfet_groen")

        user_inputs = []

        while len(user_inputs) < len(color_memory):

            previous_timestamp = get_switch_state()['lastupdated']
            timestamp = previous_timestamp

            while previous_timestamp == timestamp:

                state = get_switch_state()

                if (previous_timestamp != state['lastupdated']):

                    buttonevent = state['buttonevent']
                    timestamp = state['lastupdated']

            if (buttonevent) in (1000, 1001, 1002, 1003):
                input = 'yellow'
            elif (buttonevent) in (2000, 2001, 2002, 2003):
                input = 'green'
            elif (buttonevent) in (3000, 3001, 3002, 3003):
                input = 'blue'
            elif (buttonevent) in (4000, 4001, 4002, 4003):
                input = 'red'

            user_inputs.append(input
                               )

        if color_memory_names != user_inputs:
            log.info(color_memory_names, user_inputs)

            break

        else:

            score += 1
            service.call(domain="input_number", name="set_value",
                 value=score, entity_id="input_number.simon_says_score")
    
    color_memory = []
    color_memory_names = []

    update_score_board(input_text.simon_says_player_name, score)

    score = 0
    game_over()

