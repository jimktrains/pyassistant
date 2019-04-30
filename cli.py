#!/usr/bin/env python3

import modules

modules_to_load = [
    "weather",
    "echo",
    "out",
]

modules.load(modules_to_load)

req="echo this is a 'test' | out.file testingfile"
resp = modules.process_request(req)
print(resp)
