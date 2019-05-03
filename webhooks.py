#!/usr/bin/env python3

from werkzeug.serving import run_simple
from flask import Flask
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route("/pyassistant/receive", methods=['POST'])
def receive():
    resp = MessagingResponse()
    resp.message("The Robots are coming! Head for the hills!")
    return str(resp)

if __name__ == "__main__":
    run_simple("localhost", 5000, app)
