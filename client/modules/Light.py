#!/usr/bin/python
import random
import re
import random
from phue import Bridge

b = Bridge('192.168.1.16') # Enter bridge IP here.

WORDS = ["ALLUME", "ÉTEINS", "DE", "LA", "SALON", "CUISINE", "BAISSE", "DU"]

lights = b.get_light_objects()

#Commands for Phue
on =  {'transitiontime' : 10, 'on' : True, 'bri' : 250}
off = {'transitiontime' : 10, 'on' : False}
dim = {'transitiontime' : 75, 'bri' : 75}

def handle(text, mic, profile):

    if re.search(r'\bsalon\b', text, re.IGNORECASE):

        if re.search(r'\ballume\b', text, re.IGNORECASE):
            mic.say("J'allume la lumière du salon.")
            
            b.set_group('Salon', on)

        elif re.search(r'\béteins\b', text, re.IGNORECASE):
            mic.say("J'éteins la lumière du salon.")
            
            b.set_group('Salon', off)

        else:
            mic.say("Désolé, je n'ai pas compris.")

    elif re.search(r'\bchambre\b', text, re.IGNORECASE):

        if re.search(r'\ballume\b', text, re.IGNORECASE):
            mic.say("J'allume la lumière de la chambre")

            b.set_group('Chambre', on)

        elif re.search(r'\béteins\b', text, re.IGNORECASE):
            mic.say("J'éteins la lumière de la chambre.")

            b.set_group('Chambre', off)

        else:
            mic.say("Désolé, je n'ai pas compris.")

    elif re.search(r'\bbaisses\b', text, re.IGNORECASE):
        mic.say("Je baisses la lumières de la chambre")

        b.set_group('Chambre', dim)

    elif re.search(r'\ballume\b', text, re.IGNORECASE):
        mic.say("J'allume toutes les lumières.")

        for light in lights:
            light.on = True

    elif re.search(r'\béteins\b', text, re.IGNORECASE):

        mic.say("J'éteins toutes les lumières")

        for light in lights:
            light.on = False

    else:
        mic.say("Désolé, je n'ai pas compris.")
    
def isValid(text):
  
    if re.search(r'\ballume\b', text, re.IGNORECASE):
        return True
    elif re.search(r'\béteins\b', text, re.IGNORECASE):
        return True
    elif re.search(r'\bcuisine\b', text, re.IGNORECASE):
        return True
    elif re.search(r'\bchambre\b', text, re.IGNORECASE):
        return True
    elif re.search(r'\bbaisse\b', text, re.IGNORECASE):
        return True
    else:
        return False
