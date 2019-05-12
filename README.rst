pyassistant
===========

Command-Response framework

Allows modules to do things and pass the output to the next stage. Sort
of like a shell, but more constrained. Since ``|`` is special, it's
accepted as a command line argument but can be replaced by ``,,`` as
well.

Commands
========

pyassistant-cli CLI interface

pyassistant-wh Handles webhooks

Modules
=======

weather
  Get's the weather

cr
  Asks questions and records the responses

echo
  Repeat what's passed in

out
  Write to a file or out via SMS (using Twilio)

Actions
-------

cr.add
  Adds a Challenge to the database

cr.show\_challenges
  Shows Challenges

cr.challenge
  Provides the challenge

cr.response
  Store a response

cr.challenge\_after 
  Challenge if no response after so many hours or a negative response

echo
  Echo's the text

out.file
  Writes to a file

out.sms
  Sends an SMS via twilio

weather
  Gets the weather for a zipcode

weather.astronomical
  Gets sunrise, sunset, moon phase, and if the day is a solstice or equinox

weather.details
  Dumps a formatted version of the xml weather forecast

Examples
========

::

    pyassistant-cli weather ,, out.sms
    cd /home/jim/pyassistant && ./pyassistant-cli cr.challenge +15555555555 2 ,, out.sms

ToDo
====

-  Revisit the piping and leverage it and passing objects more heavily
-  Be less stringly typed
-  Allow for error messages and structured data to propagate
-  Add the ++ operator ( `a ++ b` creates a list from the output of `a` and `b`)
-  Rethink the `cr` module
-  Autodownload zipcode dbf file

Config (~/.config/pyassistant.ini)
==================================

::

    [storage]
    zipdbf=/home/jim/.config/pyassistant/tl_2017_us_zcta510.dbf
    skyfield=/home/jim/.config/pyassistant
    cr=/home/jim/.config/pyassistant
    cache=/home/jim/.config/pyassistant

    [out.sms]
    from_number=twilio_phone_number_to_use
    account_sid=twilio_sid
    auth_token=twilio_auth_token
    default_phonenumber=if set, the default number to send messages to

    [weather]
    default_zip=if set, the default zip to lookup weather for

SMS abbriviations
=================

To cope with the small character count of sms messages, I use the
following abbreviations:

Months
------

J
  January
F
  February
R
  March
P
  April
Y
  May
U
  June
L
  July
G
  August
S
  September
O
  October
N
  November
D
  December

Days of the Week
----------------

S
  Sunday
M
  Monday
T
  Tuesday
W
  Wednesday
H
  Thursday
F
  Friday
A
  Saturday

Moon Phases
-----------

NM
  New Moon
XC
  Waxing Crescent
FQ
  First Quarter
XG
  Waxing Gibbous
FM
  Full Moon
NG
  Waning Gibbous
LQ
  Last Quarter
NC
  Waning Crescent

Equinox and Solstice
--------------------

VE
  Vernal Equinox
SS
  Summer Solstice
AE
  Autumn Equinox
WS
  Winter Solstice

Other
-----

SR
  Sunrise
SS
  Sunset
