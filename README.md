# pyassistant
Command-Response framework

Allows modules to do things and pass the output to the next stage. Sort of like
a shell, but more constrained. Since `|` is special, it's accepted as a command line argument
but can be replaced by `,,` as well.

# Commands

pyassistant-cli
   CLI interface

pyassistant-wh
    Handles webhooks

# Modules

weather
    Get's the weather

cr
    Asks questions and records the responses

echo
    Repeat what's passed in

out
  Write to a file or out via SMS (using Twilio)

## Actions

cr.add
    Adds a Challenge to the database

cr.show_challenges
    Shows Challenges

cr.challenge
    Provides the challenge

cr.response
    Store a response

cr.challenge_after
    Challenge if no response after so many hours or a negative response

echo
    Echo's the text

out.file
    Writes to a file

out.sms
    Sends an SMS via twilio

weather
    Gets the weather for a zipcode


# Examples

    pyassistant-cli weather ,, out.sms
    cd /home/jim/pyassistant && ./pyassistant-cli cr.challenge +15555555555 2 ,, out.sms

# ToDo

* Configure storage location for databases
* Put config and databases into a folder in .config
* Autodownload zipcode dbf file
* Revisit the piping and leverage it and passing objects more heavily
 * Be less stringly typed
 * Allow for error messages to propogate

# Config (~/.config/pyassistant.ini)

    [storage]
    zipdbf=/home/jim/.config/tl_2017_us_zcta510.dbf

    [out.sms]
    from_number=twilio_phone_number_to_use
    account_sid=twilio_sid
    auth_token=twilio_auth_token
    default_phonenumber=if set, the default number to send messages to

    [weather]
    default_zip=if set, the default zip to lookup weather for
