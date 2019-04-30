#!/usr/bin/env python3

import modules
import pickle

def actions():
    return {
        'file': outfile,
        'sms': sms,
    }

@modules.with_parser("out.file", "Writes to a file")
def outfile(parser, *args):
    parser.add_argument('file', help="filename")
    parser.add_argument('text', nargs="*", help="text to write")
    args = parser.parse_args(args)

    if args.text and args.file:
        with open(args.file, "w+") as f:
            f.write(" ".join(args.text))
            return ''

@modules.with_parser("out.sms", "Sends an SMS via twilio")
def sms(parser, *args):
    parser.add_argument('phonenumber', help="phone number")
    parser.add_argument('text', nargs="*", help="text to write")
    args = parser.parse_args(args)

    if args.phonenumber and args.text:
        from twilio.rest import Client

        account_sid = modules.config['out.sms']['account_sid']
        auth_token  = modules.config['out.sms']['auth_token']
        from_number = modules.config['out.sms']['from_number']

        client = Client(account_sid, auth_token)

        result=client.messages.create(
            to=args.phonenumber,
            from_=from_number,
            body=args.text)

        return result.sid
