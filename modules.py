#!/usr/bin/env python3.7

import argparse
import shlex
import os
import sqlite3
import configparser
from pathlib import Path
import logging

logger = logging.getLogger()

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

def module(name):
    return modules[name]

def exec_request(cur_req, fstdin):
    if len(cur_req) < 1:
        return "Error: No action"
    cmd = cur_req[0]
    if cmd not in actions:
        return "Error: Action not found"

    args = []
    if len(cur_req) > 1:
        args = cur_req[1:]

    return actions[cmd](fstdin, *args)

def process_request(req):
    if type(req) is str:
        req = shlex.split(req)

    cur_req = []
    last_resp = None
    for cur_val in req:
        if cur_val in ['|', ',,']:
            last_resp = exec_request(cur_req, last_resp)
            cur_req = []
        else:
            cur_req.append(cur_val)
    if len(cur_req) != 0:
        last_resp = exec_request(cur_req, last_resp)

    return last_resp

def make_argparse(prog, description):
    parser = argparse.ArgumentParser(description=description, add_help=False, prog=prog)
    parser.add_argument('--help', action='store_true', help="prints the help")
    return parser

def with_parser(prog, description):
    def y(func):
        def x(fstdin, *args):
            args = filter(None, args)
            parser = make_argparse(prog, description)
            resp = func(parser, fstdin, *args)
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


config = configparser.ConfigParser()
dir_path = os.path.dirname(os.path.realpath(__file__))
home_dir = str(Path.home())

config_options = [
    # pyassistant.ini in current dir
    "pyassistant.ini",
    # ~/.config folder
    home_dir + "/.config/pyassistant/pyassistant.ini",
]

for config_file in config_options:
    logger.info("checking if config exists: " + config_file)
    if os.path.exists(config_file):
        break

logger.info("Trying to load config " + config_file)
config.read(config_file)

cache_db_file = config['storage']['cache'] + '/cache.sqlite3'
if not os.path.exists(cache_db_file):
    cache_db = sqlite3.connect(cache_db_file)
    cache_db.execute("create table cache (id integer primary key autoincrement, " +
                     "cache_key varchar(160) not null, " +
                     "cache_value text not null, " +
                     "expires_at datetime not null)")
    cache_db.commit()
else:
    cache_db = sqlite3.connect(cache_db_file)
