import argparse

from . import app
from .web import *

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default='config.py')
parser.add_argument("--host", default='0.0.0.0')
parser.add_argument("-p", "--port", default=5000)
parser.add_argument("-d", "--debug", action='store_true')

config_schema = {
    '$schema': "http://json-schema.org/schema#",
    'type': 'object',
    'properties': [],
    'required': [
        'BOARD_WIDTH',
        'SWITCHES',
    ]
}


def verify_config(conf):
    pass


args = parser.parse_args()
# The internal webserver forks if reloader is enabled
app.config.from_pyfile(args.config)
verify_config(app.config)
app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False, threaded=True)
