#!/usr/bin/env python3

import modules
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import dbf

ziptable = dbf.Table(modules.config['storage']['zipdbf'])
ziptable.open()
zipidx = ziptable.create_index(lambda rec: rec.zcta5ce10)

def actions():
    return {
        '': get,
        'get': get,
    }

def get_weather_et(zipcode):
    if zipcode:
        records = zipidx.search(match=(zipcode,))
        lat = None
        lon = None
        for record in records:
            lat = record.intptlat10
            lon = record.intptlon10
            break

        if lat is None or lon is None:
            return f"No lat/lon found for {zipcode}"

        cache_key = f"weather:{zipcode}"
        contents = modules.cache_get(cache_key)
        if contents is None:
            one_hour_more = datetime.utcnow() + timedelta(hours=1)
            url = f"https://forecast.weather.gov/MapClick.php?lat={lat}&lon={lon}&unit=0&lg=english&FcstType=dwml"
            contents = urllib.request.urlopen(url).read()
            modules.cache_until(cache_key, contents, one_hour_more)

        return ET.fromstring(contents)
    else:
        return None

@modules.with_parser("weather.get", "Gets the weather for a zipcode")
def get(parser, fstdin, *args):
    parser.add_argument('zipcode', nargs="?", help="zipcode to get the weather for")
    args = parser.parse_args(args)

    default_zip = None
    if 'weather' in modules.config:
        if 'default_zip' in modules.config['weather']:
            default_zip = modules.config['weather']['default_zip']
    zipcode = args.zipcode or default_zip

    root = get_weather_et(zipcode)

    if root is None:
        return "No valid zipcode provided"

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

