#!/usr/bin/env python3

import modules
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def actions():
    return {
        '': get,
        'get': get,
    }

@modules.with_parser("weather.get", "Gets the weather for a zipcode")
def get(parser, *args):
    parser.add_argument('zipcode', nargs="?", help="zipcode to get the weather for")
    args = parser.parse_args(args)

    if args.zipcode:
        # Hmm, we'll have to use
        # https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/suggest?f=json&countryCode=USA,PRI,VIR,GUM,ASM&category=Land+Features,Bay,Channel,Cove,Dam,Delta,Gulf,Lagoon,Lake,Ocean,Reef,Reservoir,Sea,Sound,Strait,Waterfall,Wharf,Amusement+Park,Historical+Monument,Landmark,Tourist+Attraction,Zoo,College,Beach,Campground,Golf+Course,Harbor,Nature+Reserve,Other+Parks+and+Outdoors,Park,Racetrack,Scenic+Overlook,Ski+Resort,Sports+Center,Sports+Field,Wildlife+Reserve,Airport,Ferry,Marina,Pier,Port,Resort,Postal,Populated+Place&maxSuggestions=10&text=15216&_=1556593710026
        # https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/find?text=15216&magicKey=dHA9MCNsb2M9NDQ2NzEzNSNsbmc9MzMjcGw9MTUzMDkwMSNsYnM9MTQ6NjU5Mzc1&f=json&_=1556593710027
        # like weather.gov or some other zipcode mapping

        contents = modules.cache_get('weather-test')
        if contents is None:
            # this feels dirty
            utc_delta = datetime.utcnow()-datetime.now()
            one_hour_more = datetime.now() + timedelta(hours=1) + utc_delta
            url = "https://forecast.weather.gov/MapClick.php?lat=40.4109&lon=-80.0244&unit=0&lg=english&FcstType=dwml"
            contents = urllib.request.urlopen(url).read()
            modules.cache_until('weather-test', contents, one_hour_more)

        root = ET.fromstring(contents)

        return (
            (get_formatted_temp(root, 'minimum', 1)) + "/" + (get_formatted_temp(root, 'maximum', 1)) + "\n" + 
            (get_weather_formatted(root, 1)) + "/" + (get_weather_formatted(root, 2))
        )


        # These were too long for sms
        for wordedForecast in root.findall('.//wordedForecast'):
            time_layout = wordedForecast.attrib['time-layout']
            first_period_name = get_time_period(root, time_layout, 1)
            first_worded_forecast = wordedForecast.find('.//text[1]').text
            if first_period_name is not None:
                first_worded_forecast = first_period_name + ": " + first_worded_forecast
            return first_worded_forecast

def get_weather_formatted(root, idx):
    weathers = root.find('.//weather')
    weather_period = get_time_period(root, weathers.attrib['time-layout'], idx)
    weather        = weathers.find('.//weather-conditions['+str(idx)+']').attrib['weather-summary']
    return weather_period + " " + weather

def get_formatted_temp(root, minmax, idx):
    temps = root.find(".//temperature[@type='"+minmax+"']")
    temp  = temps.find('./value['+str(idx)+']').text
    temp_period = get_time_period(root, temps.attrib['time-layout'], idx)
    return temp_period + " " + temp

def get_time_period(root, time_layout, idx):
    for timelayout_elm in root.findall(".//time-layout"):
        # [.='text'] in 3.7 :-\
        layout_key = timelayout_elm.find('.//layout-key')
        if time_layout == layout_key.text:
            period = timelayout_elm.find('.//start-valid-time['+str(idx)+']')
            return period.attrib['period-name']

