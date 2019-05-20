#!/usr/bin/env python3.7

import modules
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import dbf
import json
from skyfield import api
from skyfield import almanac
from skyfield.api import Loader
import math

ziptable = dbf.Table(modules.config['storage']['zipdbf'])
ziptable.open()
# Yeah, so this is slow and I need to figure out how to persist it.
zipidx = ziptable.create_index(lambda rec: rec.zcta5ce10)

loader = Loader(modules.config['storage']['skyfield'])
ts = loader.timescale()
ephem = loader('de421.bsp')

def actions():
    return {
        '': get,
        'get': get,
        'details': details,
        'astronomical': astronomical,
        'srss' : astronomical,
    }

def with_zipcode(fcn):
    def parse_with_zipcode(parser, fstdin, *args):
        default_zip = None
        if 'weather' in modules.config:
            if 'default_zip' in modules.config['weather']:
                default_zip = modules.config['weather']['default_zip']
        parser.add_argument('zipcode', nargs="?", help="zipcode to get the weather for", default=default_zip)
        return fcn(parser, fstdin, *args)

    return parse_with_zipcode

@modules.with_parser("weather.astronomical", "gets the next sunrise and sunset for zipcode")
@with_zipcode
def astronomical(parser, fstdin, *args):
    args = parser.parse_args(args)
    lat, lon = zipcode_to_latlon(args.zipcode)

    if lat and lon:

        today = datetime.today().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
        dow = day_of_week_abbriv(today)
        mon = month_abbriv(today)
        dom = today.strftime('%d')

        srss = sunrise_sunset(lat, lon)
        mp = moon_phase()
        es = equinox_solstice()


        # Just assuming the same day since we're not in the artic.
        result = f"{dow}{mon}{dom} {srss} {mp} {es}"
        return result.strip()

def zipcode_to_latlon(zipcode):
    if zipcode:
        records = zipidx.search(match=(zipcode,))
        lat = None
        lon = None
        for record in records:
            lat = float(record.intptlat10)
            lon = float(record.intptlon10)
            break
        return (lat, lon)
    return (None, None)



def get_weather_et(parser, args):
    args = parser.parse_args(args)
    lat, lon = zipcode_to_latlon(args.zipcode)

    if lat and lon:
        cache_key = f"weather:{args.zipcode}"
        contents = modules.cache_get(cache_key)
        if contents is None:
            one_hour_more = datetime.utcnow() + timedelta(hours=1)
            url = f"https://forecast.weather.gov/MapClick.php?lat={lat}&lon={lon}&FcstType=digitalDWML"
            contents = urllib.request.urlopen(url).read()
            modules.cache_until(cache_key, contents, one_hour_more)

        parser = ET.XMLParser()
        parser.entity['nbsp'] = ' '

        return ET.fromstring(contents, parser=parser)
    else:
        return None

@modules.with_parser("weather.details", "Gets the detailed weather for a zipcode")
@with_zipcode
def details(parser, fstdin, *args):
    root = get_weather_et(parser, args)
    print_tree(root)

def print_tree(root, prefix = None):
    if prefix is None:
        prefix = ''
    attribs = ''
    if len(root.attrib):
        attribs = f"({root.attrib})"
    print(f"{prefix}{root.tag}{attribs}: {root.text}")
    for child in root:
        print_tree(child, prefix + "  ")



@modules.with_parser("weather.get", "Gets the weather for a zipcode")
@with_zipcode
def get(parser, fstdin, *args):
    root = get_weather_et(parser, args)

    if root is None:
        return "No valid zipcode provided"

    #0         1         2         3         4         5         6    
    #0123456789012345678901234567890123456789012345678901234567890123456789
    #ABB CCCC DDDD /EE FFGG HH IIJJJ KK /EE...

    #                              1         1         1         1
    #7         8        9          0         1         2         3
    #0123456789012345678901234567890123456789012345678901234567890123456789
    #

    #1         1
    #4         5
    #01234567890123456789
    #

    # A = Day of Week (SMTWHFA)
    # B = Day of Month
    # C = Sunrise
    # D = Sunset
    # E = Hour for forecast
    # F = High temp
    # G = Low temp
    # H = Cloud Cover
    # I = Wind Speed
    # J = Wind Direction (N NNE NE ENE ...)
    # K = Chance of percipitation

    # Hours
    hours =     [6, 9, 12, 15, 18, 21]
    hours_lookup = []

    one_day = timedelta(days=1)
    now = datetime.today().astimezone()
    for hour in hours:
        target_time = datetime.today().astimezone().replace(hour=hour, minute=0, second=0, microsecond=0)
        if target_time < now:
            target_time += one_day
        min_diff = timedelta(hours=999)
        min_idx = None

        # There is probably a better way to do this, but since it's such a
        # small set, we're just going to do it the naive way.

        # So, the file can have multiple timelayouts, but this one doesn't
        # so, we're going to cheat.
        for time_layout in root.findall('.//time-layout'):
            for idx, node in enumerate(time_layout.findall('.//start-valid-time')):
                this_time = datetime.strptime(node.text, "%Y-%m-%dT%H:%M:%S%z")
                diff = abs(this_time - target_time)
                if diff < min_diff:
                    min_diff = diff
                    min_idx = idx
            break
        if min_idx is None:
            return f"No time found for hour {hour}"
        hours_lookup.append((target_time, min_idx))

    # Sort for nearest to now
    hours_lookup = sorted(hours_lookup, key=lambda x: x[0])

    dow = day_of_week_abbriv(now)
    mon = month_abbriv(now)
    dom = now.strftime('%d')

    response = f"{dow}{mon}{dom}"
    for hour_dt, idx in hours_lookup:
        hour = hour_dt.strftime("%H")
        temp = int(lookup(root, 'temperature[@type="hourly"]', idx))
        cloud_cover = int(lookup(root, 'cloud-amount', idx))
        wind_speed = int(lookup(root, 'wind-speed[@type="sustained"]', idx))
        wind_dir = human_dir(int(lookup(root, 'direction[@type="wind"]', idx)))
        chance_precip = int(lookup(root, 'probability-of-precipitation', idx))
        humidity = int(lookup(root, 'humidity', idx))
        # I don't like hardcoding the F unit
        response += f"\n{hour} {temp}F {cloud_cover:02}O {chance_precip:02}P {humidity:02}H {wind_speed}{wind_dir}"
    response = response.strip()
    return response

def human_dir(bearing):
    base_lookup_table = {
        0: "N",
        22: "NNE",
        45: "NE",
        67: "ENE",
        90: "E",
        112: "ESE",
        135: "SE",
        157: "SSE",
        180: "S",
        202: "SSW",
        225: "SW",
        247: "WSE",
        270: "W",
        292: "WNW",
        315: "NW",
        337: "NNW",
        360: "N",
    }

    lookup_table = {}
    low_keys = base_lookup_table.keys()
    high_keys = list(base_lookup_table.keys())[1:]
    for b,e in zip(low_keys, high_keys):
        lookup_table[int((b+e)/2) % 360] = b

    for threshold in lookup_table.keys():
        if bearing <= threshold:
            base_bearing = lookup_table[threshold]
            return base_lookup_table[base_bearing]
    return 'N'

def lookup(root, item, idx):
    node = root.find(f".//{item}/value[{idx}]")
    if node is not None:
        if 'nil' in node.attrib:
            return '0'
        return node.text


def month_abbriv(dt):
    lookup_table = {
        1: "J",
        2: "F",
        3: "R",
        4: "A",
        5: "Y",
        6: "U",
        7: "L",
        8: "G",
        9: "S",
        10: "O",
        11: "N",
        12: "D"
    }
    return lookup_table[dt.month]

def day_of_week_abbriv(dt):
    lookup_table = [
        "M",
        "T",
        "W",
        "H",
        "F",
        "A",
        "S",
    ]
    return lookup_table[dt.weekday()]

def sunrise_sunset(lat, lon):
    place = api.Topos(lat, lon)
    one_day = timedelta(days=1)
    start = datetime.today().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + one_day

    start = ts.utc(start)
    end = ts.utc(end)
    srss, sross = almanac.find_discrete(start, end, almanac.sunrise_sunset(ephem, place))

    tz = datetime.now().astimezone().tzinfo
    (sr,ss) = srss.astimezone(tz)

    t0_time = sr.strftime('%H%M')
    t0_srss = "SR" if sross[0] else "SS"
    t1_time = ss.strftime('%H%M')
    t1_srss = "SR" if sross[1] else "SS"
    return f"{t0_srss}{t0_time} {t1_srss}{t1_time}"

def moon_phase():
    lookup_table = [
        "NM",
        "FQ",
        "FM",
        "LQ",
    ]
    end = datetime.today().astimezone().replace(hour=23, minute=59, second=0, microsecond=0)
    t0 = ts.utc(end)

    mp = almanac.moon_phases(ephem)(t0)
    mp = lookup_table[mp]

    mf = almanac.fraction_illuminated(ephem, 'moon', t0)
    mf = math.ceil(mf*100)

    return f"{mp}{mf:02}"

def equinox_solstice():
    lookup_table = [
        'VE',
        'SS',
        'AE',
        'WS',
    ]
    start = datetime.today().astimezone().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end = datetime.today().astimezone().replace(month=12, day=31, hour=0, minute=0, second=0, microsecond=0)
    today = datetime.today().astimezone()
    t0 = ts.utc(start)
    t1 = ts.utc(end)
    times, events = almanac.find_discrete(t0, t1, almanac.seasons(ephem))

    tz = datetime.now().astimezone().tzinfo

    for yi, ti in zip(events, times):
        ti = ti.astimezone(tz)
        if (today.month, today.day) == (ti.month, ti.day):
            return lookup_table[yi] + ti.strftime('%H%M')
    return ''
