#!/usr/bin/env python3

import modules
import pickle

def actions():
    return {
        'file': outfile,
        'sms': sms,
    }

@modules.with_parser("out.file", "Writes to a file")
def outfile(parser, fstdin, *args):
    parser.add_argument('file', help="filename")
    parser.add_argument('text', nargs="*", help="text to write", default=fstdin)
    args = parser.parse_args(args)

    if args.text and args.file:
        with open(args.file, "w+") as f:
            f.write(" ".join(args.text))
            return ''

@modules.with_parser("out.sms", "Sends an SMS via twilio")
def sms(parser, fstdin, *args):
    if 'out.sms' not in modules.config:
        return "Must have out.sms section"
    config = modules.config['out.sms']
    if 'account_sid' not in config:
        return "Must have account_sid in out.sms section"
    if 'auth_token' not in config:
        return "Must have auth_token in out.sms section"
    if 'from_number' not in config:
        return "Must have from_number in out.sms section"
    phonenumber=None
    if 'default_phonenumber' in config:
        phonenumber=config['default_phonenumber']
    parser.add_argument('phonenumber', nargs="?", help="phone number", default=phonenumber)
    parser.add_argument('text', nargs="*", help="text to write", default=fstdin)
    args = parser.parse_args(args)


    account_sid = config['account_sid']
    auth_token  = config['auth_token']
    from_number = config['from_number']

    if phonenumber and args.text:
        from twilio.rest import Client

        client = Client(account_sid, auth_token)

        result=client.messages.create(
            to=phonenumber,
            from_=from_number,
            body=args.text)

        return result.sid
