#!/usr/bin/env python3

from gevent.pywsgi import WSGIServer
from flask import Flask
app = Flask(__name__)

@app.route("/receive")
def receive():
    return "Hello World!"


if __name__ == '__main__':
    # Debug/Development
    # app.run(debug=True, host="0.0.0.0", port="5000")
    # Production
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
