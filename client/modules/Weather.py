# -*- coding: utf-8-*-
import re
import datetime
import struct
import urllib
import feedparser
import requests
import bs4
import logging
from client.app_utils import getTimezone
from semantic.dates import DateService

WORDS = ["TEMPS", "MÉTÉO", "AUJOURD'HUI", "DEMAIN"]


def replaceAcronyms(text):
    """
    Replaces some commonly-used acronyms for an improved verbal weather report.
    """

    def parseDirections(text):
        words = {
            'N': 'nord',
            'S': 'sud',
            'E': 'est',
            'W': 'ouest',
        }
        output = [words[w] for w in list(text)]
        return ' '.join(output)
    acronyms = re.findall(r'\b([NESW]+)\b', text)

    for w in acronyms:
        text = text.replace(w, parseDirections(w))

    text = re.sub(u'&deg; C', u'degrés celsius', text)
    text = re.sub(u'km\/h', u'kilomètres par heure', text)
    text = re.sub(u'hPa', u'hecto pascal', text)

    return text


def get_locations():
    r = requests.get('http://www.wunderground.com/about/faq/' +
                     'international_cities.asp')
    soup = bs4.BeautifulSoup(r.text)
    data = soup.find(id="inner-content").find('pre').string
    # Data Stucture:
    #  00 25 location
    #  01  1
    #  02  2 region
    #  03  1
    #  04  2 country
    #  05  2
    #  06  4 ID
    #  07  5
    #  08  7 latitude
    #  09  1
    #  10  7 logitude
    #  11  1
    #  12  5 elevation
    #  13  5 wmo_id
    s = struct.Struct("25s1s2s1s2s2s4s5s7s1s7s1s5s5s")
    for line in data.splitlines()[3:]:
        row = s.unpack_from(line)
        info = {'name': row[0].strip(),
                'region': row[2].strip(),
                'country': row[4].strip(),
                'latitude': float(row[8].strip()),
                'logitude': float(row[10].strip()),
                'elevation': int(row[12].strip()),
                'id': row[6].strip(),
                'wmo_id': row[13].strip()}
        yield info


def get_forecast_by_name(location_name):
    entries = feedparser.parse("http://french.wunderground.com/auto/rss_full/%s"
                               % urllib.quote(location_name))['entries']
    if entries:
        # We found weather data the easy way
        return entries
    else:
        # We try to get weather data via the list of stations
        for location in get_locations():
            if location['name'] == location_name:
                return get_forecast_by_wmo_id(location['wmo_id'])


def get_forecast_by_wmo_id(wmo_id):
    return feedparser.parse("http://french.wunderground.com/auto/" +
                            "rss_full/global/stations/%s.xml"
                            % wmo_id)['entries']

def extractDate(text, now):
    text = text.upper()
    days = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]
    weekday = now.weekday()
    for i in range(len(days)):
        if re.search(days[i], text, re.UNICODE):
	    if i == weekday:
		result = 0
	    elif i > weekday:
		result = i-weekday
	    else:
		result = i+7-weekday
	    return {'weekday': days[i].title(), 'date': now+datetime.timedelta(days=result)}
	elif re.search("DEMAIN", text, re.UNICODE):
	    result = now+datetime.timedelta(days=1)
	    return {'weekday': days[result.weekday()].title(), 'date': result}
	elif re.search("AUJOURD'HUI", text, re.UNICODE):
	    return {'weekday': days[now.weekday()].title(), 'date': now}


def handle(text, mic, profile):
    """
    Responds to user-input, typically speech text, with a summary of
    the relevant weather for the requested date (typically, weather
    information will not be available for days beyond tomorrow).

    Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    logger = logging.getLogger(__name__)

    forecast = None
    if 'wmo_id' in profile:
        forecast = get_forecast_by_wmo_id(str(profile['wmo_id']))
    elif 'location' in profile:
        forecast = get_forecast_by_name(str(profile['location']))

    if not forecast:
        mic.say("Oups, je ne peux pas acceder à vos informations. Vérifier que vous avez bien renseigné votre localisation.")
        return

    tz = getTimezone(profile)
    now = datetime.datetime.now(tz=tz)
    extract = extractDate(text, now)
    if not extract:
        weekday = extractDate("Aujourd'hui", now)['weekday']
	date = now
    else:
        weekday = extract['weekday']
        date = extract['date']

    if date.weekday() == now.weekday():
        date_keyword = "Aujourd'hui"
    elif date.weekday() == (now.weekday() + 1) % 7:
        date_keyword = "Demain"
    else:
        date_keyword = weekday

    output = None

    for entry in forecast:
        #try:
            date_desc = entry['title'].split()[0].strip().lower()
            if date_desc == u'prévisions':
                # For global forecasts
                date_desc = entry['title'].split()[3].strip().lower()
                weather_desc = entry['summary']
		logger.debug("PREVISIONS : " + date_desc + "    " + weather_desc)
            elif date_desc == u'conditions':
                # For first item of global forecasts
		logger.debug("CONDITIONS")
                continue
            else:
                # US forecasts
                weather_desc = entry['summary'].split('-')[1]
		logger.debug("OTHER : " + weather_desc)

	    logger.debug("EGALITE ? " + weekday + " et " + date_desc.title())
            if weekday == date_desc.title():
                output = u"Les prévisions pour " + date_keyword  + u" sont : " + weather_desc + "."
                break
        #except:
            #continue

    if output:
        output = replaceAcronyms(output)
        mic.say(output)
    else:
        mic.say(
            "Désolé, j'ai eu un problème.")


def isValid(text):
    """
        Returns True if the text is related to the weather.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    text = text.lower()
    return bool(re.search(u'(météo|températures?|prévisions?|chaud|temps|froid|veste|manteau|pluie|pleut)', text, re.IGNORECASE))
