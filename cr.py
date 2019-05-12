#!/usr/bin/env python3

import modules
import os
import sqlite3

database_file = modules.config['storage']['cr'] + '/cr.sqlite3'

database = None

def actions():
    return {
        'challenge': challenge,
        'add': add_challenge,
        'response': response,
        'challenge_after': challenge_after,
        'show': show_challenges
    }


@modules.with_parser("cr.add", "Adds a Challenge to the database")
def add_challenge(parser, fstdin, *args):
    parser.add_argument('text', nargs="+", help="the text of the challenge")
    args = parser.parse_args(args)

    if args.text:
        t = (" ".join(args.text),)
        cursor = database.execute("insert into challenge (text) values (?)", t)
        database.commit()
        return cursor.lastrowid

@modules.with_parser("cr.show_challenges", "Shows Challenges")
def show_challenges(parser, fstdin, *args):
    resp = "id\ttext\n"
    for row in database.execute("select id, text from challenge"):
        resp += str(row[0]) + "\t" + row[1] + "\n";
    return resp

@modules.with_parser("cr.challenge", "Provides the challenge")
def challenge(parser, fstdin, *args):
    parser.add_argument('person', help="id for the person")
    parser.add_argument('challenge', help="id for the challenge")
    args = parser.parse_args(args)

    if args.person and args.challenge:
        database.execute("insert into challenged (person, challenge_id) values (?,?)", (args.person, args.challenge))
        database.commit()
        for row in database.execute("select text from challenge where id = ?", (args.challenge, )):
            return row[0]
        return f"Challenge {args.challenge} doesn't exist"

@modules.with_parser("cr.response", "Store a response")
def response(parser, fstdin, *args):
    parser.add_argument('person', help="id for the person")
    parser.add_argument('response', help="response")
    args = parser.parse_args(args)

    if args.person and args.response:
        cursor = database.execute("insert into responses (person, response) values (?,?)", (args.person, args.response))
        database.commit()
        return str(cursor.lastrowid)

@modules.with_parser("cr.challenge_after", "Challenge if no response after so many hours or a negative response")
def challenge_after(parser, fstdin, *args):
    parser.add_argument('person', help="id for the person")
    parser.add_argument('challenge', help="id for the challenge")
    parser.add_argument('hours', help="Ask again if this many hours without a response or a negative response")
    args = parser.parse_args(args)

    sql = ("select challenge_id " +
          "from challenged " +
          "  left join responses on responses.created_at > challenged.created_at " +
          "where " + 
          "  challenged.created_at = (" + 
          "    select max(created_at) from challenged where challenge_id = ? group by challenge_id" + 
          "  ) and " + 
          "  challenged.challenge_id = ? and " + 
          "  (24*(julianday(current_timestamp) - julianday(challenged.created_at))) > ? and " + 
          "  response is null or upper(response) in ('N', 'NO', '0')")

    if args.person and args.challenge and args.hours:
        t = (args.challenge, args.challenge, args.hours)
        for row in database.execute(sql, t):
            return challenge(args.person, args.challenge)
        return ''

if not os.path.exists(database_file):
    database = sqlite3.connect(database_file)
    database.execute("create table challenge (id integer primary key autoincrement, text varchar(160) not null)")
    database.execute("create table challenged (id integer primary key autoincrement, " + 
                     "person varchar(160) not null, " + 
                     "challenge_id integer, " + 
                     "created_at datetime default current_timestamp, " + 
                     "foreign key(challenge_id) references challenge(id))")
    database.execute("create table response (id integer primary key autoincrement, " + 
                     "person varchar(160) not null, " + 
                     "response varchar(160), " + 
                     "created_at datetime default current_timestamp)")
    database.commit()
                     
else:
    database = sqlite3.connect(database_file)
