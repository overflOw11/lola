#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import re
import random
import logging
from phue import Bridge

b = Bridge('192.168.1.16') # Enter bridge IP here.

WORDS = ["ALLUME", "ÉTEINS", "DE", "LA", "SALON", "CUISINE", "DU", "LUMIÈRES", "LUMIÈRE", "ROUGE", "VERT", "BLEU", "JAUNE", "ORANGE", "VIOLET", "ROSE", "EN"]

#Commands for Phue
on =  {'transitiontime' : 10, 'on' : True, 'bri' : 250}
off = {'transitiontime' : 10, 'on' : False}

def colors(text):
    text = text.upper()
    colors = [u"ROUGE", u"(VERT|VERRE)", u"BLEU", u"JAUNE", u"ORANGE", u"VIOLET", u"ROSE"]
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

    # Turn on the lights
    if re.search(u'(allume|mets)', text, re.UNICODE):	

        # Get the color you want to set on light
        on["xy"] = colors(text)

        if re.search(u'salon', text, re.UNICODE):
            b.set_light('Salon', on)
            mic.say("J'allume la lumière du salon.")

        elif re.search(u'chambre', text, re.UNICODE):
            b.set_light('Chambre', on)
            mic.say("J'allume la lumière de la chambre")

        else:
	    b.set_group(0, on)
	    mic.say("J'allume toutes les lumières.")

    # Turn off the lights	
    elif re.search(u'éteins', text, re.UNICODE):

	if re.search(u'salon', text, re.UNICODE):
            b.set_light('Salon', off)
            mic.say("J'éteins la lumière du salon.")

        elif re.search(u'chambre', text, re.UNICODE):
            b.set_light('Chambre', off)
            mic.say("J'éteins la lumière de la chambre")

        else:
            b.set_group(0, off)
            mic.say("J'éteins toutes les lumières.")            

    else:
        mic.say("Désolé, je n'ai pas compris.")


def isValid(text):
    text = text.lower()
    if re.search(u'allume', text, re.UNICODE):
        return True
    elif re.search(u'mets', text, re.UNICODE):
	return True
    elif re.search(u'éteins', text, re.UNICODE):
        return True
    elif re.search(u'cuisine', text, re.UNICODE):
        return True
    elif re.search(u'chambre', text, re.UNICODE):
        return True
    else:
        return False
