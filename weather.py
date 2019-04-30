#!/usr/bin/env python3

import modules

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
        return "meh, some temp, probably rain in " + args.zipcode
