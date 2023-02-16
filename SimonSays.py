import requests
import random
import time
import speech_recognition as sr
import json
url = "http://172.17.187.253/api/fAoQajpSocxzpkNodgpZ8u8LCji1epSCYSarbeXq/groups/1/action"
urlsensor = "http://172.17.187.253/api/fAoQajpSocxzpkNodgpZ8u8LCji1epSCYSarbeXq/sensors/2"

recognizer = sr.Recognizer()
microphone = sr.Microphone()
colors = []
colors_values = {
    "green": 25500,
    "red": 65535,
    "blue": 46920,
    "yellow": 11218,
    "purple": 51024,
    "white": 41136}
color_names = ["green", "red","blue","yellow","purple"]
color = []
def recognize_speech_from_mic(recognizer, microphone):
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    print("I heard you")
    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

def game_over():
    for _ in range(10):
        r = requests.put(url, json={"on":True, "sat":254, "bri":200, "hue":colors_values["red"]}) 
        time.sleep(0.2)
        r = requests.put(url, json={"on":True, "sat":72, "bri":100, "hue":colors_values["white"]}) 
        time.sleep(0.1)


while True:
    color = color_names[random.randint(0,3)]
    colors.append(color)

    for x in colors:
        r = requests.put(url, json={"on":True, "sat":254, "bri":120, "hue":colors_values[x]}) 
        time.sleep(1)
        r = requests.put(url, json={"on":True, "sat":72, "bri":120, "hue":colors_values["white"]}) 
        time.sleep(0.5)
    r = requests.put(url, json={"on":True, "sat":72, "bri":120, "hue":colors_values["white"]}) 
    print("press the buttons, | is yellow, Big * is green, small * is blue, o is red")
    antwoorden = []
    previous_state = requests.get(urlsensor).json()
    current_state = previous_state
    print("oplossing: " +"".join(colors))
    while len(colors) != len(antwoorden):
        previous_state = current_state

        while current_state == previous_state:
            current_state = requests.get(urlsensor).json()
        if str(current_state["state"].get("buttonevent")) not in ["1000", "2000", "3000", "4000"]:
            antwoorden.append(str(current_state["state"].get("buttonevent")))
            print("antwoorden: "+ "".join(antwoorden))
    #answer = input("choices colors: green,red,blue,yellow,purple \n example: yellow blue blue blue yellow \n") #recognize_speech_from_mic(recognizer, microphone)
    for i in range(len(antwoorden)):
        antwoorden[i] = antwoorden[i].replace("1002","yellow").replace("1000","yellow").replace("2002", "green").replace("2000","green").replace("3002","blue").replace("3000","blue").replace("4002","red").replace("4000","red")
    if "".join(colors) != "".join(antwoorden): 
        break
print("Jammer")
game_over()





