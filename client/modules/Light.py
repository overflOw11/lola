#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import re
import random
import logging
from phue import Bridge

b = Bridge('192.168.1.16') # Enter bridge IP here.

WORDS = ["ALLUME", "ÉTEINS", "DE", "LA", "SALON", "CUISINE", "DU", "LUMIÈRES", "LUMIÈRE", "ROUGE", "VERT", "BLEU", "JAUNE", "ORANGE", "VIOLET", "ROSE", "EN"]

lights = b.get_light_objects()

#Commands for Phue
on =  {'transitiontime' : 10, 'on' : True, 'bri' : 250}
off = {'transitiontime' : 10, 'on' : False}

def colors(text):
    text = text.upper()
    colors = [u"ROUGE", u"VERT", u"BLEU", u"JAUNE", u"ORANGE", u"VIOLET", u"ROSE"]
    values = [[0.7,0.2986], [0.4063, 0.5126], [0.1717, 0.0494], [0.5797, 0.3884], [0.6281, 0.3565], [0.2885, 0.1074], [0.395, 0.1777], [0.4596, 0.4105]]
    n = len(colors)
    for i in range(n):
	if re.search(colors[i], text, re.UNICODE):
            return values[i]
    return values[7]

def handle(text, mic, profile):
    logger = logging.getLogger(__name__)
    logger.debug(text)
    text = text.lower()
    if re.search(u'salon', text, re.UNICODE):

        if re.search(u'allume', text, re.UNICODE):
            mic.say("J'allume la lumière du salon.")
            b.set_light('Salon', {'xy': colors(text)})
            b.set_light('Salon', on)

        elif re.search(u'éteins', text, re.UNICODE):
            mic.say("J'éteins la lumière du salon.")
            b.set_light('Salon', off)

        else:
            mic.say("Désolé, pouvez vous répéter.")

    elif re.search(u'chambre', text, re.UNICODE):

        if re.search(u'allume', text, re.UNICODE):
            mic.say("J'allume la lumière de la chambre")
	    b.set_light('Chambre', {'xy': colors(text)})
            b.set_light('Chambre', on)

        elif re.search(u'éteins', text, re.UNICODE):
            mic.say("J'éteins la lumière de la chambre.")
            b.set_light('Chambre', off)
        else:
            mic.say("Je n'ai pas compris, désolé.")

    elif re.search(u'allume', text, re.UNICODE):
        mic.say("J'allume toutes les lumières.")
        for light in lights:
            light.xy = colors(text)
	    light.on = True

    elif re.search(u'éteins', text, re.UNICODE):
        mic.say("J'éteins toutes les lumières")
        for light in lights:
            light.on = False

    else:
        mic.say("Désolé, je n'ai pas compris.")
    
def isValid(text):
    text = text.lower()
    if re.search(u'allume', text, re.UNICODE):
        return True
    elif re.search(u'éteins', text, re.UNICODE):
        return True
    elif re.search(u'cuisine', text, re.UNICODE):
        return True
    elif re.search(u'chambre', text, re.UNICODE):
        return True
    else:
        return False
