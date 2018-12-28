import enum
import threading

from flask import Flask, current_app, g, jsonify, request, session
from pysnmp.hlapi import SnmpEngine, CommunityData, ContextData, ObjectIdentity, UdpTransportTarget, getCmd, setCmd
from werkzeug.exceptions import BadRequest, Unauthorized


StateLock = threading.RLock()


class GameState(enum.IntEnum):
    PREPARING = 0
    RUNNING = 1
    OVER = 2


class CellState(enum.IntEnum):
    EMPTY = 0
    PRESENT = 1
    HIT = 2


app = Flask(__package__)


@app.route('/')
def get_root():
    return ''


@app.route('/config')
def get_config():
    return jsonify(config={
        'board': {
            'width': len(current_app['INTERFACES']) / g.board_width,
            'height': current_app.conf['BOARD_WIDTH'],
        },
        'ships': current_app.conf['SHIPS'],
    })


def get_current_player():
    if 'player' not in session:
        raise Unauthorized()
    return session['player']


@app.route('/toggle', methods=['POST'])
def toggle_cell():
    data = request.json
    if not isinstance(data, dict):
        raise BadRequest("")
    if 'cell' not in data:
        raise BadRequest("Missing cell")
    try:
        cell = int(data['cell'])
    except (ValueError, TypeError):
        raise BadRequest()
    player = get_current_player()
    try:
        cell_state = g.cell_state[player][cell]
    except KeyError:
        raise BadRequest("Unknown cell")
    with StateLock:
        if g.game_state is GameState.PREPARING:
            raise BadRequest("Not in preparing state")
        g.cell_state[player] = CellState.EMPTY if cell_state is CellState.PRESENT else CellState.PRESENT


@app.route('/reset')
def reset():
    setup_state()


@app.route('/state')
def get_state(player):
    if player not in [0, 1]:
        raise BadRequest()
    other = [1, 0][player]
    return jsonify(state={
        'state': g.state,
        'own': g.game_state[player],
        'enemy': [CellState.HIT if state is CellState.HIT else CellState.EMPTY for state in g.cell_state[other]],
    })


def setup_state():
    with StateLock:
        g.board_width = current_app.conf['BOARD_WIDTH']
        interfaces = current_app['INTERFACES']
        g.board_height = len(interfaces) / g.board_width
        g.game_state = GameState.PREPARING
        g.cell_state = [
            [CellState.UNKNOWN for _ in interfaces],
            [CellState.UNKNOWN for _ in interfaces],
        ]


ifAdminStatus = (1, 3, 6, 1, 2, 1, 2, 2, 1, 7)
ifOperStatus = (1, 3, 6, 1, 2, 1, 2, 2, 1, 8)


def do_snmp_walk(player, address):
    engine = SnmpEngine()
    auth_data = CommunityData(current_app.conf.COMMUNITY, mpModel=1)
    transport = UdpTransportTarget((address, 161))
    admin_states = getCmd(
        engine, auth_data, transport, ContextData(),
        *(ObjectIdentity(ifAdminStatus, (index,)) for index in current_app.conf['INTERFACES'])
    )
    oper_states = getCmd(
        engine, auth_data, transport, ContextData(),
        *(ObjectIdentity(ifOperStatus + (index,)) for index in current_app.conf['INTERFACES'])
    )
    with StateLock:
        for cell_state, if_state in zip(g.game_state[player], oper_states):

