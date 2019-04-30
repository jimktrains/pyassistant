#!/usr/bin/env python3

import argparse
import shlex
import os
import sqlite3
import configparser

cache_db_file = "cache.sqlite3"
cache_db = None

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
    if type(req) is str:
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

def cache_until(key, value, exp):
    t = (key, value, exp)
    cache_db.execute("insert into cache (cache_key, cache_value, expires_at) values (?,?,?)", t)
    cache_db.commit()

def cache_get(key):
    flush_cache()
    for row in cache_db.execute("select cache_value from cache where cache_key = ?", (key,)):
        return row[0]

def flush_cache():
    cache_db.execute("delete from cache where current_timestamp > expires_at")
    cache_db.commit()

if not os.path.exists(cache_db_file):
    cache_db = sqlite3.connect(cache_db_file)
    cache_db.execute("create table cache (id integer primary key autoincrement, " + 
                     "cache_key varchar(160) not null, " + 
                     "cache_value text not null, " + 
                     "expires_at datetime not null)")
    cache_db.commit()
else:
    cache_db = sqlite3.connect(cache_db_file)

config = configparser.ConfigParser()
config.read('config.ini')
