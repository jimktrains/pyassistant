#!/usr/bin/env python3

import modules
import sys

modules_to_load = [
    "weather",
    "echo",
    "out",
    "cr",
]

modules.load(modules_to_load)

if len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h']:
    print("Usage: cli.py <action> [action args]")
    print("Actions:")
    for action in modules.actions.keys():
        print("\t" + action)
    sys.exit(0)

resp = modules.process_request(sys.argv[1:])
print(resp)
