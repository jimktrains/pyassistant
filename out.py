#!/usr/bin/env python3

import modules

def actions():
    return {
        'file': outfile,
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
