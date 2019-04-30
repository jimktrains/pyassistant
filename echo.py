#!/usr/bin/env python3

import modules

def actions():
    return {
        '': echo,
    }

@modules.with_parser("echo", "Echo's the text")
def echo(parser, *args):
    parser.add_argument('text', nargs="*", help="text to echo")
    args = parser.parse_args(args)

    if args.text:
        return " ".join(args.text)
