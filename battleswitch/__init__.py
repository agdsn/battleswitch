import enum
import threading

from flask import Flask, current_app, g, jsonify, request, session, url_for, redirect
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
app.config.from_json('config.json')


def board_size():
    width = current_app.config['BOARD_WIDTH']
    no_interfaces = len(current_app.config['INTERFACES'])
    assert no_interfaces % width == 0
    height = no_interfaces // width
    return (width, height)


@app.route('/')
def get_root():
    return redirect(url_for('static', filename='start.html'))


@app.route('/game')
def get_game():
    return redirect(url_for('static', filename='battleswitch.html'))


@app.route('/config')
def get_config():
    width, height = board_size()
    return jsonify(config={
        'board': {
            'width': width,
            'height': height,
        },
        'ships': current_app.config['SHIPS'],
    })


@app.route('/player', methods=['POST'])
def set_player():
    player = request.form.get('player')
    if player not in ('0', '1'):
        raise BadRequest("Invalid player")
    session['player'] = int(player)
    return redirect('/game')


def get_current_player():
    if 'player' not in session:
        raise Unauthorized()
    player = session['player']
    if player not in (0, 1):
        raise BadRequest("Invalid player")
    return player


@app.route('/toggle', methods=['POST'])
def toggle_cell():
    cell = request.form.get('cell')
    try:
        cell = int(cell)
    except (ValueError, TypeError):
        raise BadRequest()
    player = get_current_player()
    try:
        cell_state = current_app.cell_state[player][cell]
    except KeyError:
        raise BadRequest("Invalid cell")
    with StateLock:
        if current_app.game_state != GameState.PREPARING:
            raise BadRequest("Not in preparing state")
        current_app.cell_state[player][cell] = CellState.EMPTY if cell_state is CellState.PRESENT else CellState.PRESENT
    return ''


@app.route('/reset')
def reset():
    setup_state()
    return ''


@app.route('/state')
def get_state():
    player = get_current_player()
    other = [1, 0][player]
    return jsonify(state={
        'state': current_app.game_state.name,
        'own': current_app.cell_state[player],
        'enemy': [CellState.HIT if state is CellState.HIT else CellState.EMPTY for state in current_app.cell_state[other]],
    })


@app.route('/go', methods=['POST'])
def go():
    # TODO: Do some checks.
    with StateLock:
        current_app.game_state = GameState.RUNNING


def setup_state():
    interfaces = current_app.config['INTERFACES']
    with StateLock:
        current_app.game_state = GameState.PREPARING
        current_app.cell_state = [
            [CellState.EMPTY for _ in interfaces],
            [CellState.EMPTY for _ in interfaces],
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
            pass
