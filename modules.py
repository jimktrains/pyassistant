#!/usr/bin/env python3

import argparse
import shlex

modules = {}
actions = {}

def load(modules_to_load):
    for module in modules_to_load:
        modules[module] = __import__(module)

        for [action, method] in modules[module].actions().items():
            action_name = module
            if action != '':
                action_name += "." + action
            actions[action_name] = method

def exec_request(cur_req):
    print(actions.keys())
    if len(cur_req) < 1:
        return "Error: No action"
    cmd = cur_req[0]
    if cmd not in actions:
        return "Error: Action not found"

    args = []
    if len(cur_req) > 1:
        args = cur_req[1:]

    return actions[cmd](*args)

def process_request(req):
    req = shlex.split(req)

    cur_req = []
    last_resp = None
    for cur_val in req:
        if cur_val == "|":
            cur_req.append(last_resp)
            last_resp = exec_request(cur_req)
            cur_req = []
        else:
            cur_req.append(cur_val)
    if len(cur_req) != 0:
        cur_req.append(last_resp)
        last_resp = exec_request(cur_req)

    return last_resp

def make_argparse(prog, description):
    parser = argparse.ArgumentParser(description=description, add_help=False, prog=prog)
    parser.add_argument('--help', action='store_true', help="prints the help")
    return parser

def with_parser(prog, description):
    def y(func):
        def x(*args):
            args = filter(None, args)
            parser = make_argparse(prog, description)
            resp = func(parser, *args)
            if resp is None:
                return parser.format_help()
            return resp
        return x
    return y

